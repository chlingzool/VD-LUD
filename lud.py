import pickle

class main:
    def __init__(self, name='LinyNew1-l4', mode=None, **kwargs):
        #主要信息
        self.name = name
        self.label = ('VD/LUD', name, '1-l4|1.1.4x')
        self.clusters = [f'C{c:02d}t{t:03d}' for c in range(11) for t in range(256)]
        self.main = {f"C{c:02d}t{t:03d}": None for c in range(11) for t in range(256)}
        self.index = {0: self.label}
        #分区信息
        self.part = self.PART(self.label, 1000, 2816)
        #组件库
        self.tool = self.tools(self.label)
        self.storage = self.save
        self.root = 'main://'
        self.dev = self.Dev()
        self.tool.elf = self.dev.ErrorLogInFile
        #运行
        if kwargs not in [{}, None]:
            self.dev = self.Dev(open=True, **kwargs)
        else:
            self.dev = self.Dev(open=False)
        #检查
        if mode == 'load' or mode is True: self._check()
        elif mode == 'new' or mode is None: self._format()

    #类

    class Dev:
        def __init__(self, open=False, **kwargs):
            self.open = open
            self.OnlyOneFile = kwargs.get('oof', False)
            self.ErrorLogInFile = kwargs.get('elf', False)
    
    class PART:
        def __init__(self, label: tuple, OneSize: int, num: int):
            self.space = {0: (label, ('C00t000', 'C10t255'), (OneSize, OneSize*num)), 'main': ('C00t000', 'C10t255')}
            self.size = self.space[0][2][1]

    class tools:
        def __init__(self, label: tuple):
            self.label = label
            self.link_run = self.link_lexer
            self.elf = None

        def link_lexer(self, code: str, index: dict, Main: object, LL2 = False) -> str:
            values = []
            values.extend(code.split('\n'))
            for i, value in enumerate(values):
                if i == 0:
                    if value[:2] != '!L': self.Error('LinkError', 1, f'\'{value}\'不是有效的Link_code头部'); return 1
                    else: continue
                if i == 1 and value[0] != 'F': self.Error('LinkError', 2, f'第{i+1}行不是有效的Link_code'); return 2
                if i == 2 and value[0] != 'M': self.Error('LinkError', 3, f'第{i+1}行不是有效的Link_code'); return 3
                if i == 3 and value[0] != 'C': self.Error('LinkError', 4, f'第{i+1}行不是有效的Link_code'); return 4
            file = values[1][2:]; file_path = self.file_parent(file)
            if not self.file_path_check(file_path, self.index): self.Error('LinkError', 5, f'文件路径不正确'); return 5
            if len(values[2]) > 9: self.Error('LinkError', 6, f'第3行不是有效的Link_code'); return 6
            print(f'跳转到文件\'{file}\'\t{values[3][2:]}')
            if values[2][2:5] == 'LL2':
                if values[2][5:] == 'Ture': LL2 = True
                else: LL2 = False
            Main.read_file(values[1][2:], LL2)
        
        def Error(self, error: str, num: int, value: str) -> str:
            r = '\033[91m'; y = '\033[93m'; s = '\033[0m'
            print(f"{r}{error}{s}[{y}{num}{s}]: {value}")
            if self.elf is True:
                with open('error.log', 'a') as f:
                    f.write(f"{error}[{num}]: {value}\n")
            return num

        def to_bytes(self, value: str) -> bytes:
            value = str(value)
            return value.encode('utf-16', errors="replace")
        
        def re_text(self, value: bytes) -> str:
            return value.decode('utf-16', errors="ignore")
        
        def file_parent(self, path: str) -> list:
            if path[-1] != '/': path += '/'; self.Error('PathError', 2, f'已主动补全路径为\'{path}\'')
            part_and_paths = path.split(':/')
            if len(part_and_paths) != 2: self.Error('PathError', 3, f'\'{path}\'不是有效的路径'); return 3
            part = part_and_paths[0]
            if part_and_paths[1].count('/') < 1: self.Error('PathError', 3, f'\'{path}\'不是有效的路径'); return 3
            paths = part_and_paths[1].split('/')
            for i, item in enumerate(paths):
                if item == '': paths[i] = None
            paths_w = []
            for item in paths:
                if item is not None or not paths_w or paths_w[-1] is not None: paths_w.append(item)
            paths = paths_w
            output = []; output.append(part)
            for item in paths:
                if item is not None: output.append(item)
            if len(output) == 1: output.append(None)
            return output
        
        def free_space(self, part: tuple, index: dict) -> str:
            keys = [f'C{c:02d}t{t:03d}' for c in range(11) for t in range(256)]
            all_c = part[0]; all_t = part[1]
            start_c = int(all_c[1:3])
            start_t = int(all_c[4:])
            end_c = int(all_t[1:3])
            end_t = int(all_t[4:])
            for key in index.keys():
                if key == 0: continue
                if key[-1] == '/': continue
                for i in index[key][3]:
                    keys.remove(i)
            for c in range(start_c, end_c+1):
                for t in range(start_t, end_t+1):
                    if f'C{c:02d}t{t:03d}' in keys:print(f'C{c:02d}t{t:03d}'); return f'C{c:02d}t{t:03d}'
            self.Error('StorageError', 4, f'分区\'{part[0]}\'已满'); return 4
        
        def file_path_check(self, paths: list, index: dict) -> bool:
            if paths[-1] == None: return True
            for i, path in enumerate(paths):
                if i == 0: continue
                if path is None: continue
                if path[-1] != '/': path += '/'
                if path not in index.keys(): return False
                #if i > 0 and paths[i-1] is not None and index[path][1][0] != index[f'{paths[i-1]}/'][1][1]: return False
        
        def part_clusters_check(self, part_clusters: tuple, part_space: dict) -> bool:
            if not isinstance(part_clusters, tuple): return False
            if len(part_clusters) != 2: return False
            if part_clusters[0] == part_clusters[1]: return False
            start_cluster = int(part_clusters[0][1:3])
            end_cluster = int(part_clusters[1][1:3])
            start_t = int(part_clusters[0][4:])
            end_t = int(part_clusters[1][4:])
            if part_clusters in part_space.values(): return False
            for c in part_space.values():
                if len(c) != 2: continue
                c_start_cluster = int(c[0][1:3])
                c_end_cluster = int(c[1][1:3])
                c_start_t = int(c[0][4:])
                c_end_t = int(c[1][4:])
                if c_start_cluster <= start_cluster <= c_end_cluster or c_start_cluster <= end_cluster <= c_end_cluster:
                    if c_start_t <= start_t <= c_end_t or c_start_t <= end_t <= c_end_t: return False

        def type_check(self, value: any, ling_type: str) -> bool:
            if ling_type == 'cluster':
                if isinstance(value, str) and value[0] == 'C' and value[1:3].isdigit() and value[3] == 't' and value[4:].isdigit(): return True
            elif ling_type == 'o_path':
                if isinstance(value, str) and value.count('/') >= 1: return True
            elif ling_type == 'p_path':
                if isinstance(value, str) and value.count('/') >= 2 and value.count('://') == 1: return True
            elif ling_type == 'clusterId':
                if isinstance(value, int) and 0 <= value <= 2816: return True
            return False
        
        def change_cluster(self, name: str, new_clusters: tuple, part_space: dict) -> bool:
            if not isinstance(new_clusters, tuple): return False
            if len(new_clusters) != 2: return False
            if new_clusters[0] == new_clusters[1]: return False
            start_cluster = int(new_clusters[0][1:3])
            end_cluster = int(new_clusters[1][1:3])
            start_t = int(new_clusters[0][4:])
            end_t = int(new_clusters[1][4:])
            for c in part_space.values():
                if len(c) != 2: continue
                if c == part_space[name]: continue
                c_start_cluster = int(c[0][1:3])
                c_end_cluster = int(c[1][1:3])
                c_start_t = int(c[0][4:])
                c_end_t = int(c[1][4:])
                if c_start_cluster <= start_cluster <= c_end_cluster or c_start_cluster <= end_cluster <= c_end_cluster:
                    if c_start_t <= start_t <= c_end_t or c_start_t <= end_t <= c_end_t: return False

    #深层方法

    def _check(self):
        if self.dev.OnlyOneFile:
            with open(f'{self.name}.lud', 'rb') as f:
                self = pickle.load(f)
        else:
            with open('clusters.ovd', 'rb') as c, open('index.ovd', 'rb') as i, open('partinfo.ovd', 'rb') as p:
                self.main = eval(self.tool.re_text(c.read()))
                self.index = eval(self.tool.re_text(i.read()))
                self.part = pickle.load(p)
        print('self-check over')
        return 0

    def _format(self):
        if self.dev.OnlyOneFile:
            with open(f'{self.name}.lud', 'wb') as f:
                pickle.dump(self, f)
        else:
            with open('clusters.ovd', 'wb') as c, open('index.ovd', 'wb') as i, open('partinfo.ovd', 'wb') as p:
                c.write(self.tool.to_bytes(self.main))
                i.write(self.tool.to_bytes(self.index))
                pickle.dump(self, p)
        print('format VD. ok')
        return 0
    
    def save(self):
        if self.dev.OnlyOneFile:
            with open(f'{self.name}.lud', 'wb') as f:
                pickle.dump(self, f)
        else:
            with open('clusters.ovd', 'wb') as c, open('index.ovd', 'wb') as i, open('partinfo.ovd', 'wb') as p:
                c.write(self.tool.to_bytes(self.main))
                i.write(self.tool.to_bytes(self.index))
                pickle.dump(self, p)
        return 0
    
    #主要方法

    def add_f(self, name: str, parent=None, value=None):
        if parent is None: parent = self.root
        if self.tool.type_check(parent, 'p_path') is False: self.tool.Error('PathError', 3, f'\'{parent}\'不是有效的路径'); return 3
        if parent[-1] != '/': parent += '/'; self.tool.Error('PathError', 2, f'已主动补全路径为\'{parent}\'')
        if '/' in name or '\\' in name or ':' in name or '*' in name or '_' in name or '\'' in name or '\"' in name or ';' in name or '|' in name: self.tool.Error('FileError', 3, f'\'{name}\'包含非法字符'); return 3
        path = self.tool.file_parent(parent)
        if name in self.index.keys() and (path[0], path[1:]) == self.index[name][1]: self.tool.Error('FileError', 2, f'\'{name}\'已存在于\'{parent}\'中'); return 2
        if name in self.index.keys():
            while name in self.index.keys():
                name = f'{name}_'
        if self.tool.file_path_check(path, self.index) is False: self.tool.Error('PathError', 3, f'目录\'{parent}\'不存在'); return 3
        if isinstance(path, int): return path
        if path[0] not in self.part.space.keys() or path[0] == 0: self.tool.Error('PathError', 2, f'分区\'{path[0]}\'不存在'); return 2
        if value is None:
            value = ''
            if (free := self.tool.free_space(self.part.space[path[0]], self.index)) is int: return free
            self.index.setdefault(name, ('FILE', (path[0], path[1:]), (None, 0), [free]))
            self.main[free] = value
        elif len(value) <= 1000:
            if (free := self.tool.free_space(self.part.space[path[0]], self.index)) is int: return free
            self.index.setdefault(name, ('FILE', (path[0], path[1:]), (None, len(value)), [free]))
            self.main[free] = value
        else:
            need_c = int(len(value)/1000)+1
            if (free := self.tool.free_space(self.part.space[path[0]], self.index)) is int: return free
            self.index.setdefault(name, ('FILE', (path[0], path[1:]), (None, len(value)), [free]))
            self.main[free] = value[:1000]
            for i in range(1, need_c):
                if (free := self.tool.free_space(self.part.space[path[0]], self.index)) is int: return free
                self.index[name][3].append(free)
                self.main[free] = value[i*1000:(i+1)*1000]
        self.save()
        print(f'创建文件\'{name}\'成功')
        return 0
    
    def add_ph(self, name: str, parent=None):
        if parent is None: parent = self.root
        if self.tool.type_check(parent, 'p_path') is False: self.tool.Error('PathError', 3, f'\'{parent}\'不是有效的路径'); return 3
        if parent[-1] != '/': parent += '/'; self.Error('PathError', 2, f'已主动补全路径为\'{parent}\'')
        if name[-1] != '/' or name[0] == '/': self.tool.Error('FileError', 3, '目录名无效'); return 3
        path = self.tool.file_parent(parent)
        if self.tool.file_path_check(path, self.index) is False: self.tool.Error('PathError', 3, f'目录\'{parent}\'不存在'); return 3
        if name in self.index.keys() and (path[0], path[1:]) == self.index[name][1]: self.tool.Error('FileError', 2, f'\'{name}\'已存在于\'{parent}\'中'); return 2
        if '\\' in name or ':' in name or '*' in name or '_' in name or '\'' in name or '\"' in name or ';' in name or '|' in name: self.tool.Error('FileError', 3, f'\'{name}\'包含非法字符'); return 3
        while name in self.index.keys():
                name = f'{name}_'
        if isinstance(path, int): return path
        if path[0] not in self.part.space.keys() or path[0] == 0: self.tool.Error('PathError', 2, f'分区\'{path[0]}\'不存在'); return 2
        self.index.setdefault(name, ('PATH', (path[0], path[1:]), None))
        self.save()
        print(f'创建目录\'{name}\'成功')
        return 0
    
    def add_pt(self, name: str, clusters: tuple=('C00t000', 'C10t255')):
        if name in self.part.space.keys(): self.tool.Error('FileError', 2, f'分区\'{name}\'已存在'); return 2
        if '^' in name or '`' in name or '|' in name or '\\' in name or '\'' in name or '\"' in name or ';' in name or ':' in name: self.tool.Error('FileError', 3, f'\'{name}\'包含非法字符'); return 3
        while name in self.index.keys():
                name = f'{name}_'
        if self.tool.part_clusters_check(clusters, self.part.space) is False: self.tool.Error('StorageError', 4, f'分区\'{clusters}\'不合法'); return 4
        self.part.space.setdefault(name, clusters)
        self.save()
        print(f'创建分区\'{name}\'成功')
        return 0
    
    def del_f(self, name: str, kill=False):
        if name == 0: self.tool.Error('FileError', 2, f'\'{name}\'不是有效的文件名'); return 2
        file_num = [0, []]
        for key in self.index.keys():
            if key == 0 or key[-1] == '/': continue
            if name in key:
                file_num[0] += 1
                file_num[1].append((key, self.index[key][1]))
        if file_num[0] == 0: self.tool.Error('FileError', 2, f'\'{name}\'不存在'); return 2
        if file_num[0] > 1:
            print(f'\'{name}\'存在{file_num[0]}个，请选择要删除的项:\n\t {'\n\t'.join([f'{i+1}. {file_num[1][i]}' for i in range(file_num[0])])}')
            input_num = input('请输入序号：')
            if input_num.isdigit() is False: self.tool.Error('InputError', 3, '输入有误'); return 3
            if int(input_num) > file_num[0] or int(input_num) < 1: self.tool.Error('InputError', 3, '输入有误'); return 3
            for key in self.index.keys():
                if key == 0 or key[-1] == '/': continue
                if key == file_num[1][int(input_num)-1][0]:
                    self.index.pop(key)
                    if kill is True: self.main[key] = None
                    self.save()
                    print(f'删除文件\'{key}\'成功')
                    return 0
        else:
            for key in self.index.keys():
                if key == 0 or key[-1] == '/': continue
                if key == name:
                    self.index.pop(key)
                    if kill is True: self.main[key] = None
                    self.save()
                    print(f'删除文件\'{key}\'成功')
                    return 0
        self.tool.Error('FileError', 1, f'\'{name}\'?'); return 1

    def del_ph(self, name: str):
        if name == 0 or name[-1] != '/': self.tool.Error('FileError', 2, f'\'{name}\'不是有效的目录名'); return 2
        path_num = [0, []]
        for key in self.index.keys():
            if key == 0: continue
            if name in key and name.replace('/', '') not in self.index[key][1][1]:
                path_num[0] += 1
                path_num[1].append((key, self.index[key][1]))
            elif name.replace('/', '') in self.index[key][1][1]: self.tool.Error('FileError', 2, f'\"{self.index[name][1]} | {name}\"下有文件，请先删除文件后再尝试删除目录')
            if path_num[0] == 0: self.tool.Error('FileError', 2, f'\'{name}\'不存在'); return 2
            if path_num[0] > 1:
                print(f'\'{name}\'存在{path_num[0]}个，请选择要删除的项:\n\t {'\n\t'.join([f'{i+1}. {path_num[1][i]}' for i in range(path_num[0])])}')
                input_num = input('请输入序号：')
                if input_num.isdigit() is False: self.tool.Error('InputError', 3, '输入有误'); return 3
                if int(input_num) > path_num[0] or int(input_num) < 1: self.tool.Error('InputError', 3, '输入有误'); return 3
                for key in self.index.keys():
                    if key == 0: continue
                    if key == path_num[1][int(input_num)-1][0]:
                        self.index.pop(key)
                        self.save()
                        print(f'删除目录\'{key}\'成功')
                        return 0
            else:
                for key in self.index.keys():
                    if key == 0: continue
                    if key == name:
                        self.index.pop(key)
                        self.save()
                        print(f'删除目录\'{key}\'成功')
                        return 0
        self.tool.Error('FileError', 1, f'\'{name}\'?'); return 1
    
    def del_pt(self, name: str):
        if name == 0 or name not in self.part.space.keys(): self.tool.Error('FileError', 2, f'\'{name}\'不是有效的分区名'); return 2
        for key in self.index.keys():
            if key == 0: continue
            if self.index[key][1][0] == name: self.tool.Error('FileError', 2, f'分区\'{name}\'下有文件，请先删除文件后再尝试删除分区')
        self.part.space.pop(name)
        self.save()
        print(f'删除分区\'{name}\'成功')
        return 0
    
    def rename_f(self, old_name: str, new_name: str):
        if old_name == 0 or new_name == 0 or old_name == new_name: self.tool.Error('FileError', 2, f'\'{old_name}\'或\'{new_name}\'不是有效的文件名'); return 2
        if new_name in self.index.keys(): self.tool.Error('FileError', 2, f'\'{new_name}\'已存在'); return 2
        if '/' in new_name or '\\' in new_name or ':' in new_name or '*' in new_name or '_' in new_name or '\'' in new_name or '\"' in new_name or ';' in new_name or '|' in new_name: self.tool.Error('FileError', 3, f'\'{new_name}\'包含非法字符'); return 3
        file_num = [0, []]
        for key in self.index.keys():
            if key == 0 or key[-1] == '/': continue
            if old_name in key:
                file_num[0] += 1
                file_num[1].append((key, self.index[key][1]))
        if file_num[0] == 0: self.tool.Error('FileError', 2, f'\'{old_name}\'不存在'); return 2
        if file_num[0] > 1:
            print(f'\'{old_name}\'存在{file_num[0]}个，请选择要重命名的项:\n\t {'\n\t'.join([f'{i+1}. {file_num[1][i]}' for i in range(file_num[0])])}')
            input_num = input('请输入序号：')
            if input_num.isdigit() is False: self.tool.Error('InputError', 3, '输入有误'); return 3
            if int(input_num) > file_num[0] or int(input_num) < 1: self.tool.Error('InputError', 3, '输入有误'); return 3
            for key in self.index.keys():
                if key == 0 or key[-1] == '/': continue
                if key == file_num[1][int(input_num)-1][0]:
                    self.index[new_name] = self.index.pop(key)
                    self.save()
                    print(f'重命名文件\'{key}\'为\'{new_name}\'成功')
                    return 0
        else:
            for key in self.index.keys():
                if key == 0 or key[-1] == '/': continue
                if key == old_name:
                    self.index[new_name] = self.index.pop(key)
                    self.save()
                    print(f'重命名文件\'{key}\'为\'{new_name}\'成功')
                    return 0
        self.tool.Error('FileError', 1, f'\'{old_name}\'?'); return 1
    
    def rename_ph(self, old_name: str, new_name: str):
        if old_name == 0 or new_name == 0 or old_name == new_name: self.tool.Error('FileError', 2, f'\'{old_name}\'或\'{new_name}\'不是有效的目录名'); return 2
        if new_name in self.index.keys(): self.tool.Error('FileError', 2, f'\'{new_name}\'已存在'); return 2
        if '\\' in new_name or ':' in new_name or '*' in new_name or '_' in new_name or '\'' in new_name or '\"' in new_name or ';' in new_name or '|' in new_name: self.tool.Error('FileError', 3, f'\'{new_name}\'包含非法字符'); return 3
        path_num = [0, []]
        for key in self.index.keys():
            if key == 0: continue
            if old_name in key or old_name == key.replace('_', ''):
                path_num[0] += 1
                path_num[1].append((key, self.index[key][1]))
            elif old_name.replace('/', '') in self.index[key][1][1]: self.tool.Error('FileError', 2, f'\"{self.index[old_name][1]} | {old_name}\"下有文件，请先删除文件后再尝试重命名目录')
        if path_num[0] == 0: self.tool.Error('FileError', 2, f'\'{old_name}\'不存在'); return 2
        if path_num[0] > 1:
            print(f'\'{old_name}\'存在{path_num[0]}个，请选择要重命名的项:\n\t {'\n\t'.join([f'{i+1}. {path_num[1][i]}' for i in range(path_num[0])])}')
            input_num = input('请输入序号：')
            if input_num.isdigit() is False: self.tool.Error('InputError', 3, '输入有误'); return 3
            if int(input_num) > path_num[0] or int(input_num) < 1: self.tool.Error('InputError', 3, '输入有误'); return 3
            for key in self.index.keys():
                if key == 0: continue
                if key == path_num[1][int(input_num)-1][0]:
                    self.index[new_name] = self.index.pop(key)
                    self.save()
                    print(f'重命名目录\'{key}\'为\'{new_name}\'成功')
                    return 0
        else:
            for key in self.index.keys():
                if key == 0: continue
                if key == old_name:
                    self.index[new_name] = self.index.pop(key)
                    self.save()
                    print(f'重命名目录\'{key}\'为\'{new_name}\'成功')
                    return 0
        self.tool.Error('FileError', 1, f'\'{old_name}\'?'); return 1

    def change_pt(self, name: str, mode: str, *args):
        if name == 0 or name not in self.part.space.keys(): self.tool.Error('FileError', 2, f'\'{name}\'不是有效的分区名'); return 2
        if mode == 'size':
            if self.tool.type_check(args[0], 'cluster') is False: self.tool.Error('InputError', 3, '输入有误'); return 3
            if len(args) != 1 or not isinstance(args[0], tuple): self.tool.Error('InputError', 3, '输入有误'); return 3
            if self.tool.change_cluster(name, args, self.part.space) is False: self.tool.Error('StorageError', 4, f'分区\'{name}\'不合法'); return 4
            self.part.space[name] = args[0]
            self.save()
            print(f'修改分区\'{name}\'大小成功')
            return 0
        elif mode == 'name':
            if len(args) != 1 or not isinstance(args[0], str): self.tool.Error('InputError', 3, '输入有误'); return 3
            if args[0] in self.part.space.keys(): self.tool.Error('FileError', 2, f'\'{args[0]}\'已存在'); return 2
            if '^' in args[0] or '`' in args[0] or '|' in args[0] or '\\' in args[0] or '\'' in args[0] or '\"' in args[0] or ';' in args[0] or ':' in args[0]: self.tool.Error('FileError', 3, f'\'{args[0]}\'包含非法字符'); return 3
            self.part.space[args[0]] = self.part.space.pop(name)
            self.save()
            print(f'修改分区\'{name}\'名称为\'{args[0]}\'成功')
            return 0
        else:
            self.tool.Error('InputError', 3, '输入有误'); return 3

    def move_f(self, name: str, path: str):
        if self.tool.type_check(path, 'p_path') is False: self.tool.Error('InputError', 3, f'目录{path}有误'); return 3
        if name not in self.index.keys() or name == 0: self.tool.Error('FileError', 2, f'\'{name}\'不是有效的文件名'); return 2
        paths = self.tool.file_parent(path)
        if self.tool.file_path_check(paths, self.index) is False: self.tool.Error('FileError', 2, f'目录{path}不存在'); return 2
        for key in self.index.keys():
            if key == 0 or key[-1] == '/': continue
            if name in key:
                if self.index[key][1] == (paths[0], paths[1:]): self.tool.Error('FileError', 2, f'文件\'{name}\'已在目录{path}下'); return 2
                while name in self.index.keys():
                    name = f'{name}_'
        self.index[name] = self.index.pop(key)
        self.index[name] = (self.index[name][0], (paths[0], paths[1:]), self.index[name][2], self.index[name][3])
        self.save()
        print(f'移动文件\'{name}\'到目录{path}成功')
        return 0
    
    def move_ph(self, name: str, path: str):
        if self.tool.type_check(path, 'p_path') is False: self.tool.Error('InputError', 3, f'目录{path}有误'); return 3
        if name not in self.index.keys() or name == 0 or name[-1] != '/': self.tool.Error('FileError', 2, f'\'{name}\'不是有效的目录名'); return 2
        paths = self.tool.file_parent(path)
        if self.tool.file_path_check(paths, self.index) is False: self.tool.Error('FileError', 2, f'目录{path}不存在'); return 2
        for key in self.index.keys():
            if key == 0 or key[-1] == '/': continue
            if name in key:
                if self.index[key][1] == (paths[0], paths[1:]): self.tool.Error('FileError', 2, f'目录\'{name}\'已在目录{path}下'); return 2
                while name in self.index.keys():
                    name = f'{name}_'
        self.index[name] = self.index.pop(key)
        self.index[name] = (self.index[name][0], (paths[0], paths[1:]), self.index[name][2], self.index[name][3])
        self.save()
        print(f'移动目录\'{name}\'到目录{path}成功')
        return 0
    
    def change_f(self, name: str, mode: str, *args):
        File_num = [0, []]
        for key in self.index.keys():
            if key == 0 or key[-1] == '/': continue
            if name in key:
                File_num[0] += 1
                File_num[1].append((key, self.index[key][1]))
        if File_num[0] == 0: self.tool.Error('FileError', 2, f'\'{name}\'不存在'); return 2
        elif File_num[0] > 1:
            print(f'\'{name}\'存在{File_num[0]}个，请选择要修改的项:\n\t {'\n\t'.join([f'{i+1}. {File_num[1][i]}' for i in range(File_num[0])])}')
            input_num = input('请输入序号：')
            if input_num.isdigit() is False: self.tool.Error('InputError', 3, '输入有误'); return 3
            if int(input_num) > File_num[0] or int(input_num) < 1: self.tool.Error('InputError', 3, '输入有误'); return 3
            name = File_num[1][int(input_num)-1][0]
        else: name = name
        if name == 0 or name not in self.index.keys(): self.tool.Error('FileError', 2, f'\'{name}\'不是有效的文件名'); return 2
        if mode == 'word':
            if len(args) != 1 or not isinstance(args[0], str): self.tool.Error('InputError', 3, '输入有误'); return 3
            word = args[0]
            if word == '' or word is None:
                value = ''
                if (free := self.tool.free_space(self.part.space[self.index[name][1][0]], self.index)) is int: return free
                self.index.setdefault(name, ('FILE', (self.index[name][1][0], self.index[name][1][1]), (None, 0), [free]))
                self.main[free] = value
            elif len(word) <= 1000:
                value = word
                if (free := self.tool.free_space(self.part.space[self.index[name][1][0]], self.index)) is int: return free
                self.index.setdefault(name, ('FILE', (self.index[name][1][0], self.index[name][1][1]), (None, 0), [free]))
                self.main[free] = value
            else:
                value = word
                need_c = int(len(word)/1000) + 1
                if (free := self.tool.free_space(self.part.space[self.index[name][1][0]], self.index, need_c)) is int: return free
                self.index.setdefault(name, ('FILE', (self.index[name][1][0], self.index[name][1][1]), (None, 0), [free]))
                self.main[free] = value[:1000]
                for i in range(1, need_c):
                    if (free := self.tool.free_space(self.part.space[self.index[name][1][0]], self.index)) is int: return free
                    self.index[name][3].append(free)
                    self.main[free] = value[1000*(i-1):1000*i]
            self.save()
            print(f'修改文件\'{name}\'成功')
            return 0
        elif mode == 'type':
            if len(args) != 1 or not isinstance(args[0], str): self.tool.Error('InputError', 3, '输入有误'); return 3
            if args[0] not in ['FILE', 'LINK']: self.tool.Error('InputError', 3, '输入有误'); return 3
            self.index[name] = (args[0], self.index[name][1], self.index[name][2], self.index[name][3])
            self.save()
            print(f'修改文件\'{name}\'类型成功')
            return 0
        else: self.tool.Error('InputError', 3, '输入有误'); return 3

    def change_ph(self, name: str, mode: str, *args):
        print('No value!'); return 0
    
    def read_f(self, name: str, RUN=False, FF2=False):
        file_num = [0, []]
        for key in self.index.keys():
            if key == 0 or key[-1] == '/': continue
            if name in key:
                file_num[0] += 1
                file_num[1].append((key, self.index[key][1]))
        if file_num[0] == 0: self.tool.Error('FileError', 2, f'\'{name}\'不存在'); return 2
        elif file_num[0] > 1:
            print(f'\'{name}\'存在{file_num[0]}个，请选择要读取的项:\n\t {'\n\t'.join([f'{i+1}. {file_num[1][i]}' for i in range(file_num[0])])}')
            input_num = input('请输入序号：')
            if input_num.isdigit() is False: self.tool.Error('InputError', 3, '输入有误'); return 3
            if int(input_num) > file_num[0] or int(input_num) < 1: self.tool.Error('InputError', 3, '输入有误'); return 3
            name = file_num[1][int(input_num)-1][0]
        else: name = name
        if name == 0 or name not in self.index.keys(): self.tool.Error('FileError', 2, f'\'{name}\'不是有效的文件名'); return 2
        if self.index[name][0] == 'LINK':
            if RUN is False:
                value = ''
                for i in self.index[name][3]:
                    value += self.main[i]
                print(f'文件\'{name}\'(link 只读)的内容为:\n{value}')
                return value
            elif RUN is True:
                value = ''
                for i in self.index[name][3]:
                    value += self.main[i]
                a = self.tool.link_run(value, self.index, self, FF2)
                return a
        elif self.index[name][0] == 'FILE':
            value = ''
            for i in self.index[name][3]:
                value += self.main[i]
            print(f'文件\'{name}\'的内容为:\n{value}')
            return value
        else: self.tool.Error('FileError', 2, f'\'{name}\'不是有效的文件'); return 2
    
    def list_things(self, path: str) -> list | tuple:
        if self.tool.type_check(path, 'p_path') is False: self.tool.Error('InputError', 3, f'目录{path}有误'); return 3
        paths = self.tool.file_parent(path)
        if self.tool.file_path_check(paths, self.index) is False: self.tool.Error('FileError', 2, f'目录{path}不存在'); return 2
        things = []
        things_l = {0: ((paths, paths[-1]), path), 'FILE': [], 'LINK': [], 'PATH': []}
        for key in self.index.keys():
            if key == 0: continue
            if self.index[key][1] == (paths[0], paths[1:]):
                if self.index[key][0] == 'FILE':
                    print(f'{key} (文件)')
                    things_l['FILE'].append((key, self.index[key]))
                    things.append(key)
                elif self.index[key][0] == 'LINK':
                    print(f'{key} (链接)')
                    things_l['LINK'].append((key, self.index[key]))
                    things.append(key)
                elif self.index[key][0] == 'PATH':
                    print(f'{key} (目录)')
                    things_l['PATH'].append((key, self.index[key]))
                    things.append(key)
        print(f'目录{path}下共有{len(things)}项\n分别是:\t{things}')
        return things_l, things

    def find_things(self, name: str, path: str=None) -> list | tuple:
        if path is None: path = self.root
        if self.tool.type_check(path, 'p_path') is False: self.tool.Error('InputError', 3, f'目录{path}有误'); return 3
        paths = self.tool.file_parent(path)
        if self.tool.file_path_check(paths, self.index) is False: self.tool.Error('FileError', 2, f'目录{path}不存在'); return 2
        things = []
        things_l = {0: ((paths, paths[-1]), path), 'FILE': [], 'LINK': [], 'PATH': []}
        for key in self.index.keys():
            if key == 0: continue
            if self.index[key][1] == (paths[0], paths[1:]):
                if name in key:
                    if self.index[key][0] == 'FILE':
                        print(f'{key} (文件)')
                        things_l['FILE'].append((key, self.index[key]))
                        things.append(key)
                    elif self.index[key][0] == 'LINK':
                        print(f'{key} (链接)')
                        things_l['LINK'].append((key, self.index[key]))
                        things.append(key)
                    elif self.index[key][0] == 'PATH':
                        print(f'{key} (目录)')
                        things_l['PATH'].append((key, self.index[key]))
        print(f'{path}下共找到{len(things)}项\n分别是:\t{things}')
        return things_l, things
    
    def find_aTypeThings(self, name: str, path: str=None, aType: str='FILE'):
        if path is None: path = self.root
        if self.tool.type_check(path, 'p_path') is False: self.tool.Error('InputError', 3, f'目录{path}有误'); return 3
        paths = self.tool.file_parent(path)
        if self.tool.file_path_check(paths, self.index) is False: self.tool.Error('FileError', 2, f'目录{path}不存在'); return 2
        if aType not in ['FILE', 'LINK', 'PATH']: self.tool.Error('InputError', 3, '输入有误'); return 3
        things = []
        things_l = {0: ((paths, paths[-1]), path), 'file': []}
        for key in self.index.keys():
            if key == 0: continue
            if self.index[key][1] == (paths[0], paths[1:]):
                if name in key:
                    if self.index[key][0] == aType:
                        print(f'{key} ({aType})')
                        things_l['file'].append((key, self.index[key]))
                        things.append(key)
        print(f'{path}下共找到{len(things)}项\n分别是:\t{things}')
        return things_l, things

    #辅助/工具函数

    def walk(self, path: str='main://'):
        if self.tool.type_check(path, 'p_path') is False: self.tool.Error('InputError', 3, f'目录{path}有误'); return 3
        paths = self.tool.file_parent(path)
        if self.tool.file_path_check(paths, self.index) is False: self.tool.Error('FileError', 2, f'目录{path}不存在'); return 2
        self.root = path
        return 0

    def labelf(self):
        print(self.label)

    def watch(self, what: str='all'):
        if what == 'all':
            print(self.index)
            print(self.main)
        elif what == 'index':
            print(self.index)
        elif what =='main':
            print(self.main)
        elif what == 'label':
            print(self.label)
        elif what == 'root':
            print(self.root)
        elif what == 'part':
            print(self.part.space)
        elif what == 'dev':
            if self.dev.open is True:
                print(f'设备dev已打开')
                print(f'oof:\t{self.dev.OnlyOneFile}')
                print(f'elf:\t{self.dev.ErrorLogInFile}')
            else:
                print(f'设备dev未打开')
        else:
            self.tool.Error('InputError', 3, '输入有误'); return 3

if __name__ == '__main__':
    vd = main(mode=None, oof=True, elf=True) #None表示格式化，True表示加载
    vd.labelf() #显示label
    vd.watch('dev') #显示设备dev状态
    while True:
        cmd = input("\033[93m" + 'VD> ' + "\033[0m")
        if cmd in ['exit', 'quit', 'q']: break
        else:
            try:
                exec(f'vd.{cmd}')
            except Exception as e:
                print(f'Error: {e}')