import math, random
 
def generateOTP(number: int) :
    digits = "0123456789"
    OTP = ""
 
    for i in range(number) :
        OTP += digits[math.floor(random.random() * 10)]
 
    return OTP
