from datetime import datetime
import cmd

from TextMessageSender import TextMessageSender

class TextMessageInterface(cmd.Cmd):
    intro = "Welcome to the TextMessageInterface!\nType 'help' for a list of commands.\n"
    prompt = ">>> "


    def __init__(self, text_message_sender):
        super().__init__()
        self.sender = text_message_sender

    def do_send(self, arg):
        try:
            number = input("Enter phone number: ")
            msg = input("Enter message: ")

            attachments = []
            while True:
                attachment = input("Enter attachment file name (or press enter to finish): ")
                if not attachment or attachment == "" or attachment.isspace():
                    break
                attachments.append(attachment)

            if number and msg and len(attachments) > 0:
                self.sender.send_text_with_attachments(number, msg, attachments)
            else:
                print(f"sending with num: {number} and message: {msg}")
                self.sender.send_text(number, msg)

        except Exception as e:
            print(f"Error sending message: {str(e)}")

    def do_schedule(self, arg):
        try:
            number =  input("Enter phone number: ")
            msg = input("Enter message: ")
            send_time = input("Enter send time (YYYY-MM-DD HH:MM:SS): ")
            send_time = datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")

            if number and msg and send_time:
                self.sender.schedule_text(number, msg, send_time)
                print("success")
        except Exception as e:
            print(f"Error scheduling message: {str(e)}")

    def do_list(self, arg):
        if not self.sender.scheduled_messages:
            print("No scheduled messages")
        else:
            for i, msg in enumerate(self.sender.scheduled_messages):
                print(f"{i+1}. Scheduled for {msg['send_time']}")
                print(f"To: {msg['number']}")
                print(f"Message: {msg['message']}")
                print(f"Scheduled at: {msg['scheduled_at']}")
                print(f"Scheduled for: {msg['send_time']}")
                # if msg['attachments']:
                #     print(f"Attachments: {len(msg['attachments'])}")

    def do_cancel(self, arg):
        self.do_list(arg)
        try:
            if self.sender.scheduled_messages:
                index = int(input("Enter index of message to cancel: (0 to cancel): ")) - 1
                if 0 <= index < len(self.sender.scheduled_messages):
                    removed_msg = self.sender.scheduled_messages.pop(index)
                    print(f"Cancelled message to {removed_msg['number']}: {removed_msg['message']}")
                else:
                    print("Invalid selection")
        except Exception as e:
            print(f"Error canceling message: {str(e)}")

    def do_quit(self, arg):
        self.sender.running = False
        return True

    def do_help(self, arg):
        print("\nAvailable Commands:")
        print("send - Send a message immediately")
        print("schedule - Schedule a message for later")
        print("list - List all scheduled messages")
        print("cancel - Cancel a scheduled message")
        print("quit - Exit the program")
        print("help - Show this help message")

    def emptyline(self):
        pass

    def run(self):
        self.cmdloop()



def main():
    tms = TextMessageSender()
    interface = TextMessageInterface(tms)
    interface.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

        