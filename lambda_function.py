from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests, traceback, logging, boto3, json, sys, os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)
channel_secret = os.getenv("SECRET", None)
channel_access_token = os.getenv("ACCESS_TOKEN", None)
if not channel_secret or not channel_access_token:
    logger.error(
        "need to add LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN as your environmental variables."
    )
    sys.exit(1)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
logger.info(os.environ)

dynamoTableName = "personalassistant"
dynamo = boto3.resource("dynamodb")
table = dynamo.Table(dynamoTableName)


def get_userOperations(userId):
    return None


def compose_textReplyMessage(userId, userOperations, messageText):
    if messageText.startswith("add"):
        # scan the table if the user id is already in the table
        # if yes, then append the task to the task list
        # if no, then create a new item with the user id and the task
        response = table.scan(FilterExpression=Key("LineID").eq(userId))
        if response["Count"] == 0:
            # create a new item
            table.put_item(
                Item={
                    "LineID": userId,
                    "Tasks": [messageText[4:]],
                }
            )
        else:
            # update the item
            table.update_item(
                Key={
                    "LineID": userId,
                },
                UpdateExpression="SET Tasks = list_append(Tasks, :i)",
                ExpressionAttributeValues={
                    ":i": [messageText[4:]],
                },
                ReturnValues="UPDATED_NEW",
            )
        return TextSendMessage(text="已新增任務: " + messageText[4:])

    elif messageText.startswith("delete"):
        # scan the table to get the task list
        # delete the task from the task list
        # update the task list in the table
        response = table.scan(FilterExpression=Key("LineID").eq(userId))
        if response["Count"] == 0:
            return TextSendMessage(text="您尚未新增任務")
        else:
            tasks = response["Items"][0]["Tasks"]
            if messageText[7:] in tasks:
                tasks.remove(messageText[7:])
                table.update_item(
                    Key={
                        "LineID": userId,
                    },
                    UpdateExpression="SET Tasks = :i",
                    ExpressionAttributeValues={
                        ":i": tasks,
                    },
                    ReturnValues="UPDATED_NEW",
                )
                return TextSendMessage(text="已刪除任務: " + messageText[7:])
            else:
                return TextSendMessage(text="您尚未新增任務: " + messageText[7:])
    elif messageText.startswith("list"):
        response = table.scan(FilterExpression=Key("LineID").eq(userId))
        if response["Count"] == 0:
            return TextSendMessage(text="您尚未新增任務")
        else:
            tasks = response["Items"][0]["Tasks"]
            return TextSendMessage(text="您的任務清單: " + str(tasks))
    elif messageText.startswith("clear"):
        response = table.scan(FilterExpression=Key("LineID").eq(userId))
        if response["Count"] == 0:
            return TextSendMessage(text="您尚未新增任務")
        else:
            table.delete_item(
                Key={
                    "LineID": userId,
                }
            )
            return TextSendMessage(text="已清空任務清單")
    elif messageText.startswith("help"):
        return TextSendMessage(
            text="輸入 add [任務內容] 以新增任務\n輸入 delete [任務內容] 以刪除任務\n輸入 list 以查看任務清單\n輸入 clear 以清空任務清單"
        )
    else:
        return TextSendMessage(text="請輸入正確的指令，輸入 help 以查看指令說明")


def lambda_handler(event, context):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event):
        userId = event.source.user_id
        messageText = event.message.text
        userOperations = get_userOperations(userId)
        logger.info("收到 MessageEvent 事件 | 使用者 %s 輸入了 [%s] 內容" % (userId, messageText))
        line_bot_api.reply_message(
            event.reply_token,
            compose_textReplyMessage(userId, userOperations, messageText),
        )

    try:
        signature = event["headers"]["x-line-signature"]
        body = event["body"]
        handler.handle(body, signature)

    except InvalidSignatureError:
        return {"statusCode": 400, "body": json.dumps("InvalidSignature")}

    except LineBotApiError as e:
        logger.error("呼叫 LINE Messaging API 時發生意外錯誤: %s" % e.message)
        for m in e.error.details:
            logger.error("-- %s: %s" % (m.property, m.message))
        return {"statusCode": 400, "body": json.dumps(traceback.format_exc())}

    return {"statusCode": 200, "body": json.dumps("OK")}
