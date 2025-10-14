emotions = ("happy", "sad", "fear", "surprise")
result = "true" if (emotions[-1] == "happy" and len(emotions) > 3) else "false"
print(result)


emotions = ("happy", "sad", "fear", "surprise")

if emotions[-1] == "happy" and len(emotions) > 3:
    result = "true"
else:
    result = "false"

print(result)
