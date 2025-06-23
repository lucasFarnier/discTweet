textEx = """user @User
this is example text
more text"""

textExLine1 = textEx.splitlines()[0]
textExHandle = textExLine1.split('@')
print("@" + textExHandle[1])