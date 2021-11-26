import os
import re

def convert_text_to_del(ids_del_file_path: str, text_file_to_convert_path: str):
    with open(f'{ids_del_file_path}') as relations_buffer:
        relations = relations_buffer.read()
        relations_touples = [line.split("\t") for line in relations.split("\n")]
        relations_dict = {touple[1]: touple[0] for touple in relations_touples if len(touple) > 1}

    with open(f'{text_file_to_convert_path}') as f:
        train = f.read()
        train_triples = [line.split("\t") for line in train.split("\n")]
        triples_with_numeric_replacement = [[triple[0], relations_dict[triple[1]], triple[2]] for triple in
                                            train_triples if len(triple) > 2]
        lines_with_numeric_replacement = ["\t".join(line) for line in triples_with_numeric_replacement]
        file_to_write = "\n".join(lines_with_numeric_replacement)

    return file_to_write

def convert_dict_to_(path_to_dict, type_to_conver_to: str):
    with open(path_to_dict) as f:
        entities = f.read()
        if type_to_conver_to == "txt":
            entities = re.sub("\d*\t", "", entities)
        if type_to_conver_to == "del":
            path_to_dict = path_to_dict.replace("s.","ids.")
        if type_to_conver_to not in ["del","txt"]:
            print(f"{type_to_conver_to} not accepted. Choose between txt and del")
            raise ValueError
    new_file = open(path_to_dict.replace(".dict", f".{type_to_conver_to}"), "w")
    new_file.write(entities)
    new_file.close()

if __name__ == '__main__':
    cwd = os.getcwd()
    for file in [("entities","del"), ("relations","del"), ("relations","txt")]:
        convert_dict_to_(f'{cwd}/DDB14/{file[0]}.dict',file[1])

    for file in ["test","train","valid"]:
        numeric = convert_text_to_del(ids_del_file_path=f'{cwd}/DDB14/relations.dict',
                                           text_file_to_convert_path=f'{cwd}/DDB14/{file}.txt')
        dat_file = open(f"DDB14/{file}.dat", "w")
        dat_file.write(numeric)
        dat_file.close()

