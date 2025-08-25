import requests
import time

version = "0.1"
api_url = "https://api.telegram.org/bot"

class LiotelBot:
    def __init__(self):
        self.token = None
        self.commands = {}

    def _register_command(self, index, cmd, reply):
        self.commands[index] = (cmd, reply)

    def add_command(self, cmd):
        self._register_command(1, cmd, None)

    def reply_command(self, reply):
        if 1 in self.commands:
            cmd, _ = self.commands[1]
            self._register_command(1, cmd, reply)

    def __getattr__(self, name):
        if name.startswith("add_command"):
            try:
                index = int(name.replace("add_command", ""))
            except:
                raise AttributeError(f"{name} اشتباهه")

            def wrapper(cmd):
                self._register_command(index, cmd, None)
            return wrapper

        if name.startswith("reply_command"):
            try:
                index = int(name.replace("reply_command", ""))
            except:
                raise AttributeError(f"{name} اشتباهه")

            def wrapper(reply):
                if index in self.commands:
                    cmd, _ = self.commands[index]
                    self._register_command(index, cmd, reply)
            return wrapper

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def run_bot(self):
        if not self.token:
            print(f"[Liotel v{version}] ❌ خطا: توکن تنظیم نشده است.")
            return

        print(f"ربات Liotel در حال اجراست... (نسخه: {version})")
        print("دستورات تعریف شده:")
        for idx, (cmd, reply) in self.commands.items():
            print(f"{idx}: {cmd} → {reply if reply else 'بدون پاسخ'}")

        offset = 0
        while True:
            try:
                response = requests.get(api_url + self.token + "/getUpdates", params={
                    "offset": offset + 1,
                    "timeout": 10
                })
                data = response.json()

                if not data.get("ok"):
                    print(f"[Liotel v{version}] ⚠️ خطا در دریافت آپدیت‌ها:", data)
                    time.sleep(5)
                    continue

                for update in data.get("result", []):
                    offset = update["update_id"]
                    message = update.get("message", {})
                    text = message.get("text", "").strip("/")
                    chat_id = message.get("chat", {}).get("id")

                    for _, (cmd, reply) in self.commands.items():
                        if text == cmd and reply:
                            requests.get(api_url + self.token + "/sendMessage", params={
                                "chat_id": chat_id,
                                "text": reply
                            })

            except requests.exceptions.ConnectionError:
                print(f"[Liotel v{version}] 🚨 خطا: اتصال به اینترنت برقرار نیست!")
                time.sleep(5)
            except Exception as e:
                print(f"[Liotel v{version}] ❗ خطای ناشناخته: {e}")
                time.sleep(5)