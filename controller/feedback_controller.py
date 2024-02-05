from case_controller import CaseController


class FeedbackController(CaseController):
    def start(self, message):
        self.controller.sendMessage(message.from_user.id, self.special_phrases.give_feedback)


    def processTextMessage(self, message):
        self.controller.sendMessage(self.admin_id, self.special_phrases.got_feedback)
        self.controller.forwardMessage(message, self.admin_id)
        self.controller.sendMessage(message.from_user.id, self.special_phrases.thanks)


    def finish(self, message):
        self.controller.finishActiveScenario(message.from_user.id)
