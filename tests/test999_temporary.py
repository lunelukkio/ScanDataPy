class Handler:
    """Handlerの基底クラス"""

    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    def handle(self, request):
        if self._next_handler:
            return self._next_handler.handle(request)
        return None


class ConcreteHandler1(Handler):
    """具体的な処理を行うハンドラ1"""

    def handle(self, request):
        if request == "request1":
            return f"ConcreteHandler1が処理しました: {request}"
        else:
            return super().handle(request)


class ConcreteHandler2(Handler):
    """具体的な処理を行うハンドラ2"""

    def handle(self, request):
        if request == "request2":
            return f"ConcreteHandler2が処理しました: {request}"
        else:
            return super().handle(request)


class ConcreteHandler3(Handler):
    """具体的な処理を行うハンドラ3"""

    def handle(self, request):
        if request == "request3":
            return f"ConcreteHandler3が処理しました: {request}"
        else:
            return super().handle(request)


# 動的なリストを使用してチェーンを構築
handler_list = [ConcreteHandler1(), ConcreteHandler2(), ConcreteHandler3()]

# チェーンのスタートを設定
mod_starter = Handler()
current_handler = mod_starter

# チェーンの構築
for handler in handler_list:
    current_handler = current_handler.set_next(handler)

# チェーンの確認
print(mod_starter.handle("request1"))  # 出力: ConcreteHandler1が処理しました: request1
print(mod_starter.handle("request2"))  # 出力: ConcreteHandler2が処理しました: request2
print(mod_starter.handle("request3"))  # 出力: ConcreteHandler3が処理しました: request3
print(mod_starter.handle("unknown"))   # 出力: None (どのハンドラも処理しない場合)
