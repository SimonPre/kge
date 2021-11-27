import os
import re
from typing import List
import yaml


def convert_to_nested_lists(path: str) -> List[list]:
    with open(f'{path}') as buffer:
        objects = buffer.read()
        return [line.split("\t") for line in objects.split("\n")]


def convert_to_dict(list_of_touples: List[list]) -> dict:
    return {tuple_[1]: tuple_[0] for tuple_ in list_of_touples if len(tuple_) > 1}


def convert_text_to_del(relation_ids_path: str,
                        node_ids_path: str,
                        text_file_to_convert_path: str):
    relations_lists = convert_to_nested_lists(relation_ids_path)
    relations_dict = convert_to_dict(relations_lists)

    nodes_lists = convert_to_nested_lists(node_ids_path)
    nodes_dict = convert_to_dict(nodes_lists)


    with open(f'{text_file_to_convert_path}') as f:
        train = f.read()
        train_triples = [line.split("\t") for line in train.split("\n")]
        triples_with_numeric_replacement = [
            [nodes_dict[triple[0]], relations_dict[triple[1]], nodes_dict[triple[2]]]
            for triple
            in train_triples
            if len(triple) > 2
        ]
        lines_with_numeric_replacement = ["\t".join(line) for line in triples_with_numeric_replacement]
        file_to_write = "\n".join(lines_with_numeric_replacement)

    return file_to_write


def convert_dict_to_(path_to_dict: str, type_to_convert_to: str):
    with open(path_to_dict) as f:
        entities = f.read()
        if type_to_convert_to == "txt":
            entities = re.sub("\d*\t", "", entities)
        if type_to_convert_to == "del":
            if "entities" in path_to_dict:
                path_to_dict = path_to_dict.replace("ies.", "y_ids.")
            elif "relations" in path_to_dict:
                path_to_dict = path_to_dict.replace("s.", "_ids.")

        if type_to_convert_to not in ["del", "txt"]:
            print(f"{type_to_convert_to} not accepted. Choose between txt and del")
            raise ValueError
    new_file = open(path_to_dict.replace(".dict", f".{type_to_convert_to}"), "w")
    new_file.write(entities)
    new_file.close()


def count_elements_in_file(path: str):
    return len(convert_to_nested_lists(path))


def create_dataset_yaml(path: str, name: str):
    inner_dict = {"name": name,
                  "num_entities": count_elements_in_file(f"{path}/entities.txt"),
                  "num_relations": count_elements_in_file(f"{path}/relations.txt")}

    for split_type in ["test", "train", "valid"]:
        # toDO: Need to figure out "without_unseen" means, and how to sample
        inner_dict[f"file.{split_type}.type"] = "triples"
        inner_dict[f"file.{split_type}.filename"] = f"{split_type}.del"
        inner_dict[f"file.{split_type}.split_type"] = split_type
        inner_dict[f"file.{split_type}.size"] = count_elements_in_file(f"{path}/{split_type}.del")

    output_dict = {"dataset": inner_dict}
    with open(f'{path}/dataset.yaml', 'w') as outfile:
        yaml.dump(output_dict, outfile, default_flow_style=False)


if __name__ == '__main__':
    cwd = os.getcwd()
    for dataset in ["DDB14", "NELL995"]:
        print(dataset)
        for file in [("entities", "del"), ("relations", "del"), ("relations", "txt"), ("entities", "txt")]:
            convert_dict_to_(f'{cwd}/{dataset}/{file[0]}.dict', file[1])

        for file in ["test", "train", "valid"]:
            numeric = convert_text_to_del(relation_ids_path=f'{cwd}/{dataset}/relations.dict',
                                          node_ids_path=f'{cwd}/{dataset}/entities.dict',
                                          text_file_to_convert_path=f'{cwd}/{dataset}/{file}.txt')
            dat_file = open(f"{dataset}/{file}.del", "w")
            dat_file.write(numeric)
            dat_file.close()

        create_dataset_yaml(path=f'{cwd}/{dataset}', name=dataset)
