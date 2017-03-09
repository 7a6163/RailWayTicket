# encoding: utf-8
class ReturnMsg:
    captchaErr = "驗證碼錯誤"
    IdErr = "身份證字號錯誤"
    NoSeat = "此期間訂票額滿，\n或無指定條件之車次"
    NoTrain = "【該時段、該車種已訂票額滿】\n─ 請改訂其他時段、車種乘車票"
    DateErr = "訂票日期錯誤或內容格式錯誤"
    NoReturn = "查無回傳資料"
    @staticmethod
    def success(match=None):
        if match is not None:
            return str.format("您的車票已訂到\n電腦代碼:{} \n車次:{}  車種:{}",
                                match.group('code'), match.group('trainNumber'),
                                match.group('kind').encode('utf-8'))
        else:
            return "您的車票已訂到"

a = ReturnMsg.captchaErr

print(a is not ReturnMsg.captchaErr)