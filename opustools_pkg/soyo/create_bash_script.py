from os import walk, listdir
from os.path import isfile, join

'''
    documents : 1 pdf file from OPUS 
    xces file : alignment information file
'''


def get_xces_file_list(files_path):
    xces_file_list = [f for f in listdir(files_path) if isfile(join(files_path, f))]
    xces_file_list.sort(key=lambda f: int(f[:-4]))
    return xces_file_list


def create_arg_base(directory):
    default = "opus_read  --download_dir /home/diego/PycharmProjects/my_fairseq/soyo/orig/EMEA_orig/  --source de  --target en  --write_mode normal "
    arg_list = [default]
    arg_list.append("--directory")
    arg_list.append(directory)
    arg_list.append("--alignment_file")
    base_bash_arg = " ".join(arg_list)
    return base_bash_arg


def generate_bash_script_list(xces_files, base_bash_arg, alignment_file_dir):
    bash_arg_list = []
    for xces in xces_files:
        command_line = [base_bash_arg]
        command_line.append(alignment_file_dir+xces)
        command_line.append("--write")
        command_line.append(xces[:-4])
        bash_arg = " ".join(command_line)
        bash_arg_list.append(bash_arg)
    return bash_arg_list


def generate_bash_script(bash_arg_list, file_name):
    with open(file_name, "w") as txt_file:
        for line in bash_arg_list:
            txt_file.write("".join(line) + "\n")


xces_files_dir = '/home/diego/PycharmProjects/my_fairseq/soyo/orig/EMEA_orig/xces_files/'
save_dir = '/home/diego/PycharmProjects/my_fairseq/soyo/orig/EMEA_orig/xmlfiles_per_doc/'
alignment_file_dir = "/home/diego/PycharmProjects/my_fairseq/soyo/orig/EMEA_orig/xces_files/"
directory = 'EMEA'


xces_files = get_xces_file_list(xces_files_dir)
base_bash_arg = create_arg_base(directory)
print(base_bash_arg)
bash_arg_list = generate_bash_script_list(xces_files, base_bash_arg, alignment_file_dir)
generate_bash_script(bash_arg_list, "run_EMEA.sh")