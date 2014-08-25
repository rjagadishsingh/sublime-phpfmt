import os
import os.path
import shutil
import sublime
import sublime_plugin
import subprocess
from os.path import dirname, realpath


def dofmt(eself, eview):
    self = eself
    view = eview
    s = sublime.load_settings('phpfmt.sublime-settings')
    debug = s.get("debug", False)
    psr = s.get("psr1_and_2", False)
    psr1 = s.get("psr1", False)
    psr2 = s.get("psr2", False)
    indent_with_space = s.get("indent_with_space", False)
    disable_auto_align = s.get("disable_auto_align", False)
    php_bin = s.get("php_bin", "php")
    formatter_path = os.path.join(dirname(realpath(sublime.packages_path())), "Packages", "phpfmt", "codeFormatter.php")

    uri = view.file_name()
    dirnm, sfn = os.path.split(uri)
    ext = os.path.splitext(uri)[1][1:]

    if debug:
        print("phpfmt:", uri)

    if "php" != ext:
        return False

    cmd_lint = [php_bin,"-l",uri];
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(cmd_lint, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False, startupinfo=startupinfo)
    else:
        p = subprocess.Popen(cmd_lint, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False)
    lint_out, lint_err = p.communicate()

    if(p.returncode==0):
        cmd_fmt = [php_bin]

        if debug:
            cmd_fmt.append("-ddisplay_errors=0")

        cmd_fmt.append(formatter_path)

        if psr:
            cmd_fmt.append("--psr")

        if psr1:
            cmd_fmt.append("--psr1")

        if psr2:
            cmd_fmt.append("--psr2")

        if indent_with_space:
            cmd_fmt.append("--indent_with_space")

        if disable_auto_align:
            cmd_fmt.append("--disable_auto_align")

        cmd_fmt.append(uri)

        uri_tmp = uri + "~"

        if debug:
            print("cmd_fmt: ", cmd_fmt)

        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmd_fmt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False, startupinfo=startupinfo)
        else:
            p = subprocess.Popen(cmd_fmt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirnm, shell=False)
        res, err = p.communicate()
        if err:
            if debug:
                print("err: ", err)
        else:
            if int(sublime.version()) < 3000:
                with open(uri_tmp, 'w+') as f:
                    f.write(res)
            else:
                with open(uri_tmp, 'bw+') as f:
                    f.write(res)
            if debug:
                print("Stored:", len(res), "bytes")
            shutil.move(uri_tmp, uri)
            sublime.set_timeout(revert_active_window, 50)
    else:
        print("lint error: ", lint_out)

def revert_active_window():
    sublime.active_window().active_view().run_command("revert")


class phpfmt(sublime_plugin.EventListener):
    def on_post_save(self, view):
        s = sublime.load_settings('phpfmt.sublime-settings')
        format_on_save = s.get("format_on_save", True)

        if format_on_save and int(sublime.version()) < 3000:
            self.on_post_save_async(view)

    def on_post_save_async(self, view):
        s = sublime.load_settings('phpfmt.sublime-settings')
        format_on_save = s.get("format_on_save", True)
        if format_on_save:
            dofmt(self, view)

class FmtSelectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        dofmt(self, self.view)

