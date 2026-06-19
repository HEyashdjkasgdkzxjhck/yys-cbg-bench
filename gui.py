#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
号来 - AI 数据导出工具 (GUI)
"""

import json
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# 确保能找到 modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CODE_DIR = os.path.join(SCRIPT_DIR, 'code')
sys.path.insert(0, CODE_DIR)

import cbg_bench


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('号来 - AI 数据导出')
        self.geometry('720x540')
        self.resizable(True, True)
        self.minsize(560, 400)

        self._build_ui()

    def _build_ui(self):
        # --- 顶部输入区 ---
        frm_top = ttk.Frame(self, padding=(12, 10, 12, 0))
        frm_top.pack(fill=tk.X)

        ttk.Label(frm_top, text='藏宝阁链接:').pack(anchor=tk.W)

        frm_url = ttk.Frame(frm_top)
        frm_url.pack(fill=tk.X, pady=(2, 0))

        self.var_url = tk.StringVar()
        ent_url = ttk.Entry(frm_url, textvariable=self.var_url)
        ent_url.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ent_url.bind('<Return>', lambda e: self._run(lite=False))

        # --- 按钮区 ---
        frm_btn = ttk.Frame(frm_top)
        frm_btn.pack(fill=tk.X, pady=(8, 0))

        self.btn_full = ttk.Button(
            frm_btn, text='完整导出 (JSON + 报告)',
            command=lambda: self._run(lite=False))
        self.btn_full.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_lite = ttk.Button(
            frm_btn, text='精简导出 (仅 JSON)',
            command=lambda: self._run(lite=True))
        self.btn_lite.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_open = ttk.Button(
            frm_btn, text='打开输出目录',
            command=self._open_output)
        self.btn_open.pack(side=tk.RIGHT)

        # --- 选项区 ---
        frm_opts = ttk.Frame(frm_top)
        frm_opts.pack(fill=tk.X, pady=(6, 0))

        self.var_dump_raw = tk.BooleanVar(value=True)
        self.var_dump_ai = tk.BooleanVar(value=True)

        ttk.Checkbutton(frm_opts, text='dump-raw',
                        variable=self.var_dump_raw).pack(side=tk.LEFT)
        ttk.Checkbutton(frm_opts, text='dump-ai',
                        variable=self.var_dump_ai).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Label(frm_opts, text='输出目录:').pack(side=tk.LEFT, padx=(16, 4))
        self.var_dump_dir = tk.StringVar(value='output')
        ttk.Entry(frm_opts, textvariable=self.var_dump_dir,
                  width=14).pack(side=tk.LEFT)

        # --- 日志区 ---
        frm_log = ttk.Frame(self, padding=(12, 8, 12, 10))
        frm_log.pack(fill=tk.BOTH, expand=True)

        self.txt_log = scrolledtext.ScrolledText(
            frm_log, wrap=tk.WORD, font=('Consolas', 10),
            state=tk.DISABLED, bg='#1e1e1e', fg='#cccccc',
            insertbackground='#cccccc', selectbackground='#264f78')
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # --- 底部状态栏 ---
        self.var_status = tk.StringVar(value='就绪')
        ttk.Label(self, textvariable=self.var_status,
                  relief=tk.SUNKEN, padding=(8, 2)).pack(fill=tk.X, side=tk.BOTTOM)

    def _log(self, msg):
        self.txt_log.configure(state=tk.NORMAL)
        self.txt_log.insert(tk.END, msg + '\n')
        self.txt_log.see(tk.END)
        self.txt_log.configure(state=tk.DISABLED)

    def _set_running(self, running):
        state = tk.DISABLED if running else tk.NORMAL
        self.btn_full.configure(state=state)
        self.btn_lite.configure(state=state)
        self.var_status.set('正在处理...' if running else '就绪')

    def _open_output(self):
        dump_dir = os.path.join(SCRIPT_DIR, self.var_dump_dir.get())
        if not os.path.isdir(dump_dir):
            dump_dir = SCRIPT_DIR
        os.startfile(dump_dir)

    def _run(self, lite=False):
        url = self.var_url.get().strip()
        if not url:
            messagebox.showwarning('提示', '请输入藏宝阁链接')
            return

        self.txt_log.configure(state=tk.NORMAL)
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.configure(state=tk.DISABLED)

        self._set_running(True)

        dump_raw = self.var_dump_raw.get()
        dump_ai = self.var_dump_ai.get()
        dump_dir = self.var_dump_dir.get().strip() or 'output'

        t = threading.Thread(target=self._worker,
                             args=(url, lite, dump_raw, dump_ai, dump_dir),
                             daemon=True)
        t.start()

    def _worker(self, url, lite, dump_raw, dump_ai, dump_dir):
        try:
            cbg_bench.DUMP_RAW = dump_raw
            cbg_bench.DUMP_AI = dump_ai
            cbg_bench.DUMP_DIR = os.path.join(SCRIPT_DIR, dump_dir)
            cbg_bench.LITE = lite
            cbg_bench.DATA_SOURCE = {}
            cbg_bench.DATA_RESULT = []
            cbg_bench.callback_cio = lambda msg: self.after(0, self._log, msg)

            self.after(0, self._log, '正在抓取数据...')
            cbg_bench.thread_fetch_config = threading.Thread(
                target=cbg_bench.fetch_config)
            cbg_bench.thread_fetch_config.start()

            cbg_bench.fetch_data(url)

            if dump_raw:
                self.after(0, self._log, '[dump-raw] 保存原始数据...')
                cbg_bench.dump_raw_data()

            self.after(0, self._log, '正在分析...')
            cbg_bench.bench()

            if dump_ai:
                self.after(0, self._log, '[dump-ai] 生成 AI 数据...')
                cbg_bench.dump_ai_profile()

            self.after(0, self._log, '保存报告...')
            cbg_bench.save(url)

            self.after(0, self._log, '\n--- 完成 ---')
            self.after(0, self.var_status.set, '完成')

        except Exception as e:
            self.after(0, self._log, '\n[错误] ' + str(e))
            self.after(0, self.var_status.set, '出错')
        finally:
            self.after(0, self._set_running, False)


if __name__ == '__main__':
    multiprocessing_freeze_support = getattr(
        __import__('multiprocessing'), 'freeze_support', lambda: None)
    multiprocessing_freeze_support()
    app = App()
    app.mainloop()
