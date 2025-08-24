# -*- coding: utf-8 -*-

import sqlite3
import sys
import time
import logging
import re
import argparse
import os
from tabulate import tabulate
from logging.handlers import RotatingFileHandler

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer
from prompt_toolkit.styles.pygments import style_from_pygments_dict
from pygments.token import Token
from pygments.styles import get_style_by_name




# 导入国际化和配置模块
# 通过将项目 src 目录添加到 sys.path，我们可以使用绝对路径来导入模块
# 这解决了在直接运行脚本时出现的“attempted relative import with no known parent package”问题
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from sqlite3_prompt.i18n import setup_translation, get_supported_languages, get_translator, _
from sqlite3_prompt.helpers_config import config


def setup_language():
    """每次启动时都允许用户选择或确认语言"""
    _ = get_translator()
    supported_langs = get_supported_languages()
    lang_list = list(supported_langs.items())

    # 1. 获取当前配置的语言
    current_lang_code = config.get('language')

    # 打印欢迎信息
    print("-" * 60)
    print(_("欢迎使用 datawork 系列的 SQLite3 交互式终端。"))
    print("-" * 60)

    # 2. 准备显示语言选项

    print("请选择您的语言 / Please select your language:")
    default_index = -1
    for i, (lang_code, lang_name) in enumerate(lang_list, 1):
        if lang_code == current_lang_code:
            print(f"  {i}. {lang_name} ({lang_code}) <-- 当前/Current")
            default_index = i
        else:
            print(f"  {i}. {lang_name} ({lang_code})")

    # 3. 构建提示信息
    if default_index != -1:
        # 使用 .format() 来避免 f-string 在 i18n 中的问题，即使这里不翻译也保持一致性
        prompt_message = "\n输入序号 (直接回车选择 '{current_lang_name}') / Enter number (Press Enter for '{current_lang_name}'): ".format(
            current_lang_name=supported_langs[current_lang_code]
        )
    else:
        prompt_message = "\n请输入选项序号 (1-{num_choices}) / Enter option number (1-{num_choices}): ".format(num_choices=len(lang_list))

    # 4. 获取用户输入
    while True:
        try:
            choice = input(prompt_message).strip()

            # 情况一：用户直接回车 (且有默认值)
            if not choice and default_index != -1:
                # 提醒当前使用的语言
                # print(f"\n当前语言已设置为 / Current language set to: {supported_langs[current_lang_code]}")
                break  # 使用当前配置，无需任何操作

            # 情况二：用户输入了数字
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(lang_list):
                    selected_lang_code = lang_list[choice_num - 1][0]
                    selected_lang_name = lang_list[choice_num - 1][1]

                    # 仅当选择的语言与当前配置不同时，才更新配置文件
                    if selected_lang_code != current_lang_code:
                        config.set('language', selected_lang_code)
                        print(f"\n语言已更新为 / Language updated to: {selected_lang_name}")
                    # else:
                    #     print(f"\n当前语言已设置为 / Current language set to: {supported_langs[current_lang_code]}")
                    break
                else:
                    print("无效的选项，请重新输入。 / Invalid option, please try again.")
            
            # 情况三：无效输入 (非数字，或在没有默认值时直接回车)
            else:
                print("无效的输入，请输入数字。 / Invalid input, please enter a number.")

        except (KeyboardInterrupt, EOFError):
            print("\n\n操作取消。 / Operation cancelled.")
            sys.exit(0)

    # 5. 根据最终的语言选择来设置翻译
    setup_translation()
    # 打印一个空行和分隔符，让后续输出更清晰
    print()
    print("-" * 60)


# --- 以下所有函数与之前相同 ---
# 日志、历史文件、配置文件都放到配置目录。2025-08-23 17:47:58
def setup_logging():
    logger = logging.getLogger()
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # 写入到配置目录
        base_dir = os.path.dirname(config.config_path)
        os.makedirs(base_dir, exist_ok=True)
        log_path = os.path.join(base_dir, 'sqlite3-prompt.log')

        # 从配置读取（可选），无则使用默认
        max_bytes = config.get('log_max_bytes', 1 * 1024 * 1024)  # 1MB
        backup_count = config.get('log_backup_count', 5)          # 保留5份

        file_handler = RotatingFileHandler(
            log_path,
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)







def print_error_report(sql, error):
    _ = get_translator()
    print(f"\n{'='*20} [{_('SQL执行错误')}] {'='*20}")
    print(_("| 错误类型: {error_type}\n| 错误信息: {error}").format(error_type=type(error).__name__, error=error))
    
    # 修复：将待翻译字符串与装饰性边框分离开，以避免 KeyError
    print(_("| 你尝试执行的SQL语句是:\n| > {sql}").format(sql=sql))
    print(f"{'='*58}\n")

    ai_helper_prompt = f"""
{_('我正在使用SQLite3，尝试执行以下SQL语句时遇到了问题：')}
**{_('SQL语句:')}**\n```sql\n{sql}\n```\n**{_('收到的错误信息是:')}**\n```\n{error}\n```
{_('请帮我分析可能的原因，并提供修改建议。')}"""
    print(f"📋 [{_('AI助手模板')}] {_('你可以复制以下内容向AI提问：')}")
    print(f"{'-' * 60}\n{ai_helper_prompt.strip()}\n{'-' * 60}\n")

def execute_sql(cursor, sql_statement):
    _ = get_translator()
    logging.info(_("执行SQL: {sql}").format(sql=sql_statement))
    start_time = time.time()
    try:
        # V1.0 升级：使用 executescript 来支持未来可能的多语句
        # 对于单条语句，它的行为和 execute 一样，但更健壮
        cursor.executescript(sql_statement)
        # 注意：executescript 不返回结果，我们需要用另一条查询获取
        # 但为了保持简单，我们假设学习场景下一次只执行一条查询
        # 如果需要显示结果，我们还需要进一步处理
        # 暂时简化：对于可能返回结果的语句，我们还是用 execute
        # 这是一个权衡，我们先用一个简单的逻辑
        is_select_or_pragma = sql_statement.strip().upper().startswith(('SELECT', 'PRAGMA'))
        
        if is_select_or_pragma and ';' in sql_statement:
            # 对于单条查询，只执行分号前的部分
            single_statement = sql_statement.split(';')[0] + ';'
            cursor.execute(single_statement)
            rows = cursor.fetchall()
            if rows:
                headers = [desc[0] for desc in cursor.description]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
                print(_("\n查询到 {row_count} 行。").format(row_count=len(rows)))
            else: # 例如 PRAGMA foreign_keys = ON;
                 print(_("命令执行成功。"))
        else: # 对于 INSERT, UPDATE, CREATE 等
            print(_("命令执行成功。"))

    except sqlite3.Error as e:
        print_error_report(sql_statement, e)
        logging.error(_("SQL执行失败: {error} | SQL: {sql}").format(error=e, sql=sql_statement))
    finally:
        duration = time.time() - start_time
        print(_("(操作耗时: {duration:.4f} 秒)").format(duration=duration))




def _human_size(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"

def _get_db_abs_path(conn):
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA database_list;")
        rows = cur.fetchall()
        for __, name, file_path in rows:
            if name == 'main':
                return os.path.abspath(file_path) if file_path else "(memory)"
    except sqlite3.Error:
        pass
    return "(unknown)"

def _print_ai_database_brief(conn):
    _ = get_translator()
    cur = conn.cursor()

    db_path = _get_db_abs_path(conn)
    size_str = "(unknown)"
    if db_path not in ("(memory)", "(unknown)") and os.path.exists(db_path):
        try:
            size_str = _human_size(os.path.getsize(db_path))
        except Exception:
            pass

    print("-" * 60)
    print(_("数据库基础信息（可提供给AI，方便AI理解当前数据库结构与状态）"))
    print("-" * 60)
    print(_("数据库文件: {p}").format(p=db_path))
    print(_("文件大小: {s}").format(s=size_str))
    print(_("SQLite版本: {v}").format(v=sqlite3.sqlite_version))

    try:
        cur.execute("PRAGMA database_list;")
        dblist = cur.fetchall()
        if dblist:
            print(_("已附加的数据库:"))
            for __, name, f in dblist:
                print(f"  - {name}: {f or '(memory)'}")
    except sqlite3.Error:
        pass

    try:
        cur.execute("PRAGMA user_version;")
        user_version = cur.fetchone()[0]
        print(_("PRAGMA user_version: {uv}").format(uv=user_version))
    except sqlite3.Error:
        pass

    try:
        cur.execute("PRAGMA foreign_keys;")
        fk_on = cur.fetchone()[0]
        print(_("PRAGMA foreign_keys: {fk}").format(fk=fk_on))
    except sqlite3.Error:
        pass

    print("\n" + "-" * 60)
    print(_("对象概览（表/视图）"))
    print("-" * 60)
    try:
        cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name;")
        objects = cur.fetchall()
        if not objects:
            print(_("无用户定义的表或视图。"))
        else:
            for name, typ in objects:
                print(f"- {typ.upper()}: {name}")
    except sqlite3.Error as e:
        print(_("获取对象概览失败: {e}").format(e=e))

    print("\n" + "-" * 60)
    print(_("详细信息（逐表）"))
    print("-" * 60)
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            print(_("\n表: {t}").format(t=t))
            try:
                cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (t,))
                create_sql = cur.fetchone()
                print(_("建表语句:"))
                print((create_sql[0] if create_sql and create_sql[0] else "(unknown)") + "\n")
            except sqlite3.Error:
                print(_("无法获取建表语句。\n"))

            try:
                cur.execute(f"SELECT COUNT(*) FROM {t};")
                count = cur.fetchone()[0]
                print(_("行数: {c}").format(c=count))
            except sqlite3.Error:
                print(_("行数: (unknown)"))

            try:
                cur.execute(f"PRAGMA foreign_key_list({t});")
                fks = cur.fetchall()
                if fks:
                    print(_("外键:"))
                    for fk in fks:
                        # (id, seq, table, from, to, on_update, on_delete, match)
                        id_val, seq_val, ref_table, col_from, col_to, on_update, on_delete, match = fk
                        print(f"  - {t}.{col_from} -> {ref_table}.{col_to} (update:{on_update}, delete:{on_delete}, match:{match})")
                else:
                    print(_("外键: 无"))
            except sqlite3.Error:
                print(_("外键: (unknown)"))

            try:
                cur.execute(f"PRAGMA index_list({t});")
                idxs = cur.fetchall()
                if idxs:
                    print(_("索引:"))
                    for idx in idxs:
                        # (seq, name, unique, origin, partial)
                        __, idx_name, unique, *__rest = idx
                        print(f"  - {idx_name} (unique:{bool(unique)})")
                        try:
                            cur.execute(f"PRAGMA index_info({idx_name});")
                            cols = [r[2] for r in cur.fetchall()]
                            print(f"    columns: {', '.join(cols)}")
                        except sqlite3.Error:
                            pass
                else:
                    print(_("索引: 无"))
            except sqlite3.Error:
                print(_("索引: (unknown)"))
    except sqlite3.Error as e:
        print(_("获取详细信息失败: {e}").format(e=e))

    print("\n" + "-" * 60)
    print(_("以上信息可直接复制给 AI，用于理解当前数据库结构与状态。"))

def _print_paths_info():
    _ = get_translator()
    base_dir = os.path.dirname(config.config_path)
    config_path = config.config_path
    log_path = os.path.join(base_dir, 'sqlite3-prompt.log')
    history_path = os.path.join(base_dir, '.sqlite3-prompt-history')

    print("-" * 60)
    print(_("路径信息"))
    print("-" * 60)
    print(_("配置文件: {p}").format(p=config_path))
    print(_("日志文件: {p}").format(p=log_path))
    print(_("历史文件: {p}").format(p=history_path))
    print(_("当前工作目录: {p}").format(p=os.getcwd()))



def handle_dot_command(command, conn):
    _ = get_translator()
    # ... 此函数与 V0.9 完全相同 ...
    logging.info(_("执行元命令: {command}").format(command=command))
    parts = command.lower().split()
    cmd = parts[0]
    start_time = time.time()
    if cmd in [".exit", ".quit", ".exit;", ".quit;"]: return "exit" # 兼容带分号的输入。2025-08-23 16:31:27



    elif cmd in [".info", ".info;"]:
        _print_ai_database_brief(conn)
        duration = time.time() - start_time
        print(_("(操作耗时: {duration:.4f} 秒)").format(duration=duration))
    elif cmd in [".paths", ".paths;"]:
        _print_paths_info()
        duration = time.time() - start_time
        print(_("(操作耗时: {duration:.4f} 秒)").format(duration=duration))




    elif cmd == ".tables" or cmd == ".tables;": # 支持 .tables 和 .tables; 两种形式。兼容。2025-08-23 16:31:27
        print(_("数据库中的所有表:"))
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        # 这里元命令自己就是完整的，直接调用execute
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows:
            headers = [desc[0] for desc in cursor.description]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            print(_("\n查询到 {row_count} 行。").format(row_count=len(rows)))
        duration = time.time() - start_time
        print(_("(操作耗时: {duration:.4f} 秒)").format(duration=duration))
    elif cmd == ".help" or cmd == ".help;": # 支持 .help 和 .help; 两种形式。兼容。2025-08-23 16:31:27
        # 获取基础帮助文本
        help_text = _("""欢迎使用帮助！当前支持的元命令:
  .tables          显示所有表名。
  .info            显示数据库基础信息，以便快速理解数据库结构与状态。
  .paths           显示配置文件、日志文件、历史文件等路径信息。
  .help            显示此帮助信息。
  .exit, .quit     退出本程序。""")
        

        # 附加上下文信息
        # style_name = 'monokai' # 注意：这里硬编码了样式名，未来可优化
        additional_info = _("""
提示: SQL语句必须以分号 (;) 结尾才能执行。
""")


        print(help_text)
        print(additional_info)
        duration = time.time() - start_time
        print(_("(操作耗时: {duration:.4f} 秒)").format(duration=duration))
    else:
        print(_("无法识别的元命令: '{command}'。输入 .help 查看帮助。").format(command=command))
        duration = time.time() - start_time
        print(_("(操作耗时: {duration:.4f} 秒)").format(duration=duration))
    return True

# SmartCompleter 类与 V0.9 完全相同
class SmartCompleter(Completer):
    def __init__(self, conn):
        self.conn = conn
        self.keywords = [
            # SQL Keywords (sorted alphabetically)
            'ADD', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC', 'ATTACH', 'AUTOINCREMENT',
            'BEGIN', 'BETWEEN', 'BLOB', 'BY', 'CASE', 'CAST', 'CHECK', 'COLUMN',
            'COMMIT', 'CONSTRAINT', 'CREATE', 'CROSS', 'DEFAULT', 'DELETE', 'DESC',
            'DETACH', 'DISTINCT', 'DROP', 'ELSE', 'END', 'EXCEPT', 'EXISTS',
            'EXPLAIN', 'FOREIGN', 'FROM', 'GLOB', 'GROUP', 'HAVING', 'IN', 'INNER',
            'INSERT', 'INTEGER', 'INTERSECT', 'INTO', 'IS', 'ISNULL', 'JOIN',
            'KEY', 'LEFT', 'LIKE', 'LIMIT', 'NOT', 'NOTNULL', 'NULL', 'OFFSET',
            'ON', 'OR', 'ORDER', 'OUTER', 'PRIMARY', 'PRAGMA', 'REAL', 'REFERENCES',
            'REINDEX', 'RELEASE', 'RENAME', 'RIGHT', 'ROLLBACK', 'SAVEPOINT',
            'SELECT', 'SET', 'TABLE', 'TEXT', 'THEN', 'TRANSACTION', 'TRIGGER',
            'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW',
            'WHEN', 'WHERE', 'WITH',

            # other keywords
            'IF', 

            # Specific PRAGMA values
            'foreign_keys', 'table_info', 'index_list', 'user_version',

            # Dot commands
            '.tables', '.info', '.paths', '.help', '.exit', '.quit'
        ]
        self.table_cache = None
        self.column_cache = {}

    def _get_tables(self):
        if self.table_cache is None:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                self.table_cache = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error: self.table_cache = []
        return self.table_cache

    def _get_columns(self, table_name):
        if table_name not in self.column_cache:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name});")
                self.column_cache[table_name] = [row[1] for row in cursor.fetchall()]
            except sqlite3.Error: self.column_cache[table_name] = []
        return self.column_cache[table_name]

    def _extract_table_context(self, text):
        match = re.search(r'\b(?:from|join|update)\s+([a-zA-Z0-9_]+)', text, re.IGNORECASE)
        if match: return match.group(1)
        return None

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)
        words = text.lower().split()

        pragma_match = re.search(r'table_info\(\s*([^)]*)$', text, re.IGNORECASE)
        if pragma_match:
            partial_table = pragma_match.group(1)
            for table in self._get_tables():
                if table.lower().startswith(partial_table.lower()):
                    yield Completion(table, start_position=-len(partial_table))
            return

        column_triggers = ['where', 'by', 'and', 'or', 'on', 'set']
        if words and words[-1] in column_triggers or (len(words) > 1 and words[-2] in column_triggers):
            table_name = self._extract_table_context(text)
            if table_name:
                for col in self._get_columns(table_name):
                    if col.lower().startswith(word.lower()):
                        yield Completion(col, start_position=-len(word))
                return

        table_triggers = ['from', 'update', 'join', 'into']
        if words and (words[-1] in table_triggers or (len(words) > 1 and words[-2] in table_triggers)):
            for table in self._get_tables():
                if table.lower().startswith(word.lower()):
                    yield Completion(table, start_position=-len(word))
            return
            
        for keyword in self.keywords:
            if keyword.lower().startswith(word.lower()):
                yield Completion(keyword, start_position=-len(word))


# --- V1.0 核心改动：全新的 REPL 逻辑 ---
# 日志、历史文件、配置文件都放到配置目录。2025-08-23 17:47:58
def run_repl(conn):
    _ = get_translator()
    base_style_name = 'monokai'
    style_dict = get_style_by_name(base_style_name).styles
    style_dict[Token.Literal.String] = '#e6db74'
    final_style = style_from_pygments_dict(style_dict)
    

    # 历史文件放到配置目录
    base_dir = os.path.dirname(config.config_path)
    os.makedirs(base_dir, exist_ok=True)
    history_path = os.path.join(base_dir, '.sqlite3-prompt-history')

    session = PromptSession(
        history=FileHistory(history_path),
        auto_suggest=AutoSuggestFromHistory(),
        style=final_style,
    )


    # session = PromptSession(
    #     history=FileHistory('.sqlite3-prompt-history'),
    #     auto_suggest=AutoSuggestFromHistory(),
    #     style=final_style,
    # )
    
    completer = SmartCompleter(conn)

    # 整合欢迎语
    # print(_("欢迎使用 datawork 系列的 SQLite3 交互式终端。"))
    print(_("输入 .help 获取帮助, .exit 退出。"))


    # V1.0 核心逻辑：语句缓冲区
    sql_buffer = ""

    while True:
        try:
            # 根据缓冲区是否为空，决定主/次提示符
            prompt_str = "sqlite> " if not sql_buffer else "   ...> "
            
            line = session.prompt(
                prompt_str, 
                lexer=PygmentsLexer(SqlLexer), 
                completer=completer
            )
            
            # 如果缓冲区为空，且输入的是元命令，则直接处理
            if not sql_buffer and line.strip().startswith('.'):
                 if handle_dot_command(line.strip(), conn) == "exit":
                     break
                 continue

            # 将新输入的一行加入缓冲区
            if sql_buffer:
                sql_buffer += "\n" + line
            else:
                sql_buffer = line

            # 检查缓冲区内容是否以分号结尾 (忽略末尾空白)
            if sql_buffer.strip().endswith(';'):
                command_to_run = sql_buffer
                logging.info(f"执行缓冲区SQL: {command_to_run}")
                
                execute_sql(conn.cursor(), command_to_run)
                conn.commit()
                
                # 执行完毕，清空缓冲区
                sql_buffer = ""
            
        except KeyboardInterrupt: # Ctrl+C 可以清空当前正在输入的语句
            if sql_buffer:
                print(_("\n当前输入已取消。"))
                sql_buffer = ""
            else:
                # 如果缓冲区是空的，Ctrl+C 没意义，直接换行
                print()
                continue
        except EOFError:
            print(_("\n再见！"))
            break

def main():
    setup_logging()
    
    # 首先设置语言
    setup_language()

    _ = get_translator()
    
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(
        description=_("一个支持自动补全和语法高亮的SQLite3命令行终端。"),
        epilog=_("如果没有提供数据库文件路径，程序会提示你输入。")
    )
    parser.add_argument(
        "db_path",
        nargs='?',  # '?' 表示这个参数是可选的
        default=None,
        help=_("要连接的SQLite3数据库文件的路径。")
    )
    args = parser.parse_args()

    db_path = args.db_path
    
    # 如果未通过命令行提供路径，则提示用户输入，直到获得有效输入
    if db_path is None:
        # 从配置中加载历史记录
        db_history_list = config.get('db_history', [])
        # prompt_toolkit 的 history 是栈式，所以需要反向加载
        history = InMemoryHistory()
        for path in reversed(db_history_list):
            history.append_string(path)
        
        # 创建一个专门用于路径输入的会
        path_session = PromptSession(history=history)

        # 先打印完整的提示信息
        print(_("请输入数据库路径"))
        print(_("1. 可使用 ↑ ↓ 方向键选择历史记录\n2. 可输入 sqlite3 数据库完整路径，以打开已有数据库\n3. 也可直接输入名称，在当前目录创建一个新数据库，如：my_database.db"))

        while True:
            try:
                # 使用一个更简洁的提示符
                user_input = path_session.prompt('> ')
                path = user_input.strip()
                
                # 1. 检查输入是否为空
                if not path:
                    print(_("数据库路径不能为空，请重新输入。"))
                    continue
                
                # 2. 检查是否以 .db 结尾
                if not path.lower().endswith('.db'):
                    print(_("数据库路径必须以 .db 结尾，请重新输入。"))
                    continue

                # 所有检查通过
                db_path = path
                break  # 输入有效，跳出循环
            except (KeyboardInterrupt, EOFError):
                print(_("\n操作取消。"))
                sys.exit(0)

    # 在连接前，检查文件是否存在，并给出相应提示
    is_new_db = not os.path.exists(db_path)
    if is_new_db:
        print(_("注意: 文件 '{path}' 不存在, 将会创建一个新的数据库。").format(path=db_path))

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        # 获取数据库文件的绝对路径
        db_abs_path = os.path.abspath(db_path)
        
        # 只要成功连接，就将路径添加到历史记录
        config.add_to_db_history(db_abs_path)
        
        logging.info(_("成功连接到数据库: {db_path}").format(db_path=db_abs_path))
        
        # 根据是新建还是打开，显示不同信息
        if is_new_db:
            print(_("已成功创建并连接到新数据库: {db_path}").format(db_path=db_abs_path))
        else:
            print(_("已成功连接到数据库: {db_path}").format(db_path=db_abs_path))
        
        # 打印一个空行以分隔
        print()

        run_repl(conn)
    except sqlite3.Error as e:
        logging.critical(_("数据库连接失败: {error}").format(error=e))
        print(_("数据库连接失败: {error}").format(error=e), file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            logging.info(_("数据库连接已关闭。"))
            print(_("数据库连接已关闭。"))

if __name__ == "__main__":
    main() 