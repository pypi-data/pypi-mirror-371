def formatComma(number):
    return "{:,}".format(number)

def execute(playerData):
    count = playerData.get("_supercoolhiddencommand", 0) + 1
    playerData["_supercoolhiddencommand"] = count

    if count > 100000:
        print("OKAY NO MORE. THIS IS GETTING OUT OF HAND.")
        return
    elif count == 100000:
        print(f"genuinely impressive. you used this command {formatComma(count)} times. are you okay?")
    elif count >= 1000:
        print("BRO YOU USED THIS COMMAND OVER 1,000 TIMES WHAT IS WRONG WITH YOU??")
    elif count >= 100:
        print("you have used this command over 100 times. stop.")
    elif count == 100:
        print("you really used this command 100 times? wow.")
    else:
        print("wow you found the super cool hidden command. good job")