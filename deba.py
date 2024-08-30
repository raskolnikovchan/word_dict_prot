import re

def remove_number_prefix(s):
    return re.sub(r'^\d+ ', '', s)

# テストケース
x = "集合：1か所に集まること"
y = "2 単語：ああああああああああああ"
z = "単語：ああああああああああああ"

print(remove_number_prefix(x))  # 出力: 単語：ああああああああああああああああ
print(remove_number_prefix(y))  # 出力: 単語：ああああああああああああ
print(remove_number_prefix(z))  