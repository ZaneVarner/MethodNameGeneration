# %%
print(2)
# %%
a = 3
# %%
source_folder_path = '../data/code2seq/java-small/training'
source_file_path = \
    f'{source_folder_path}/elasticsearch/CJKFilterFactoryTests.java'

# %%
import javalang
# %%
with open(source_file_path, encoding='utf-8') as source_file:
    source = source_file.read()
# %%
tree = javalang.parse.parse(source)
# %%
documentation = '^%^&%&%'
try:
    start = documentation.find(next(filter(str.isalnum, documentation)))
except StopIteration:
    print('whooopsss')
# %%
next(filter(str.isalnum, documentation))
# %%