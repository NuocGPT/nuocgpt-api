from enum import Enum


class ErrorMessage(str, Enum):
    INCORRECT_EMAIL_OR_PASSWORD = "INCORRECT_EMAIL_OR_PASSWORD"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_NOT_VERIFIED = "USER_NOT_VERIFIED"
    OTP_INCORRECT_OR_EXPIRED = "OTP_INCORRECT_OR_EXPIRED"
    TOKEN_INVALID_OR_EXPIRED = "TOKEN_INVALID_OR_EXPIRED"


irrelevant_keywords = [
    "war",
    "politics",
    "religion",
    "chiến tranh",
    "chính trị",
    "tôn giáo"
]

class IrrelevantMessage(str, Enum):
    VI = "Xin lỗi, tôi không được lập trình để cung cấp thông tin về các chủ đề nhạy cảm hoặc không liên quan. Phạm vi nhiệm vụ của tôi được giới hạn trong việc cung cấp thông tin liên quan đến xâm nhập mặn ở khu vực Đồng bằng sông Cửu Long. Tuy nhiên, nếu bạn có bất kỳ câu hỏi nào liên quan đến các giải pháp về nước và xâm nhập mặn, tôi sẽ sẵn lòng hỗ trợ bạn."
    EN = "Sorry, I am not programmed to provide information about out sensitive or irrelevant topics. My scope of duties is limited to providing information related to saltwater intrusion in the Mekong Delta region. However, if you have any questions regarding water and saltwater intrusion solutions, I would be happy to assist you."
