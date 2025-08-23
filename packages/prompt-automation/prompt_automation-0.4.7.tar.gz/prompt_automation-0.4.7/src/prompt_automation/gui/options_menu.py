"""Shared Options menu construction for Prompt Automation GUI.

Centralizes menu item definitions so single-window and legacy selector views
stay in sync. Keeps logic lightweight and defensive (GUI only; failures are
logged but not raised).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

from ..errorlog import get_logger
from .constants import INFO_CLOSE_SAVE

_log = get_logger(__name__)


def configure_options_menu(
    root,
    selector_view_module,
    selector_service,
    *,
    include_global_reference: bool = True,
    include_manage_templates: bool = True,
    extra_items: Callable[[Any, Any], None] | None = None,
) -> Dict[str, Callable[[], None]]:  # pragma: no cover - GUI heavy
    """(Re)build the Options menu and attach to ``root``.

    Returns mapping of accelerator sequences to callables so caller can bind.
    """
    import tkinter as tk

    try:
        menubar = root.nametowidget(root['menu']) if root and root['menu'] else tk.Menu(root)
    except Exception:  # pragma: no cover - best effort
        menubar = tk.Menu(root)

    # Replace entire menubar to avoid duplicate cascades
    new_menubar = tk.Menu(root)
    opt = tk.Menu(new_menubar, tearoff=0)
    accelerators: Dict[str, Callable[[], None]] = {}

    # Reset reference files
    def _reset_refs():
        try:
            from tkinter import messagebox
            if selector_service.reset_file_overrides():
                messagebox.showinfo("Reset", "Reference file prompts will reappear.")
            else:
                messagebox.showinfo("Reset", "No overrides found.")
        except Exception as e:
            _log.error("Reset refs failed: %s", e)
    opt.add_command(label="Reset reference files", command=_reset_refs, accelerator="Ctrl+Shift+R")
    accelerators['<Control-Shift-R>'] = _reset_refs

    # Manage overrides
    def _manage_overrides():
        try:
            selector_view_module._manage_overrides(root, selector_service)  # type: ignore[attr-defined]
        except Exception as e:
            _log.error("Manage overrides failed: %s", e)
    opt.add_command(label="Manage overrides", command=_manage_overrides)

    # Edit global exclusions
    def _edit_exclusions():
        try:
            selector_view_module._edit_exclusions(root, selector_service)  # type: ignore[attr-defined]
        except AttributeError:
            _log.warning("_edit_exclusions not available in selector view module")
        except Exception as e:
            _log.error("Edit exclusions failed: %s", e)
    opt.add_command(label="Edit global exclusions", command=_edit_exclusions)
    opt.add_separator()

    # New template wizard
    def _open_wizard():
        try:
            from .new_template_wizard import open_new_template_wizard
            open_new_template_wizard()
        except Exception as e:
            _log.error("Template wizard failed: %s", e)
    opt.add_command(label="New template wizard", command=_open_wizard)

    # Manage templates dialog
    if include_manage_templates:
        def _open_manage_templates():  # pragma: no cover
            import tkinter as tk
            from tkinter import messagebox
            from ..menus import PROMPTS_DIR
            import json
            win = tk.Toplevel(root)
            win.title("Manage Templates")
            win.geometry("760x500")
            win.resizable(True, True)
            cols = ("id","title","rel")
            tree = tk.Treeview(win, columns=cols, show="headings")
            widths = {"id":60, "title":230, "rel":420}
            for c in cols:
                tree.heading(c, text=c.upper()); tree.column(c, width=widths[c], anchor='w')
            vs = tk.Scrollbar(win, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=vs.set)
            tree.pack(side='left', fill='both', expand=True); vs.pack(side='right', fill='y')
            def _load():
                tree.delete(*tree.get_children())
                for p in sorted(PROMPTS_DIR.rglob('*.json')):
                    try: data = json.loads(p.read_text())
                    except Exception: continue
                    tree.insert('', 'end', values=(data.get('id',''), data.get('title', p.stem), str(p.relative_to(PROMPTS_DIR))))
            def _preview(event=None):
                sel = tree.selection();
                if not sel: return
                rel = tree.item(sel[0])['values'][2]
                path = PROMPTS_DIR / rel
                try: raw = path.read_text()
                except Exception as e:
                    messagebox.showerror('Preview', f'Unable: {e}'); return
                pv = tk.Toplevel(win); pv.title(f"Template: {rel}"); pv.geometry('700x600')
                from .fonts import get_display_font
                txt = tk.Text(pv, wrap='word', font=get_display_font(master=pv)); txt.pack(fill='both', expand=True)
                txt.insert('1.0', raw); txt.config(state='disabled')
                pv.bind('<Escape>', lambda e: (pv.destroy(), 'break'))
            def _delete():
                sel = tree.selection();
                if not sel: return
                rel = tree.item(sel[0])['values'][2]
                path = PROMPTS_DIR / rel
                from tkinter import messagebox
                if not messagebox.askyesno('Delete', f'Delete template {rel}?'): return
                try: path.unlink()
                except Exception as e: messagebox.showerror('Delete', f'Failed: {e}'); return
                _load()
            def _new():
                try:
                    from .new_template_wizard import open_new_template_wizard
                    open_new_template_wizard(); _load()
                except Exception as e: messagebox.showerror('Wizard', f'Failed: {e}')
            tree.bind('<Double-1>', _preview)
            btns = tk.Frame(win, pady=6); btns.pack(fill='x')
            tk.Button(btns, text='New', command=_new).pack(side='left')
            tk.Button(btns, text='Delete', command=_delete).pack(side='left', padx=(6,0))
            tk.Button(btns, text='Refresh', command=_load).pack(side='left', padx=(6,0))
            tk.Button(btns, text='Close', command=win.destroy).pack(side='right')
            win.bind('<Escape>', lambda e: (win.destroy(),'break'))
            win.bind('<Control-Return>', lambda e: (win.destroy(),'break'))
            _load()
        opt.add_command(label='Manage templates', command=_open_manage_templates)
        opt.add_separator()

    # Shortcut manager
    def _open_shortcut_manager():
        try:
            selector_view_module._manage_shortcuts(root, selector_service)  # type: ignore[attr-defined]
        except Exception as e:
            _log.error("Shortcut manager failed: %s", e)
            try:
                from tkinter import messagebox
                messagebox.showerror("Shortcut Manager", f"Failed to open: {e}")
            except Exception:
                pass
    opt.add_command(label="Manage shortcuts / renumber", command=_open_shortcut_manager, accelerator="Ctrl+Shift+S")
    accelerators['<Control-Shift-S>'] = _open_shortcut_manager

    # Global reference file manager
    if include_global_reference:
        from .collector.persistence import reset_global_reference_file, get_global_reference_file
        from ..renderer import read_file_safe
        def _open_global_reference_manager():  # pragma: no cover
            import tkinter as tk
            from tkinter import filedialog
            win = tk.Toplevel(root)
            win.title("Global Reference File")
            win.geometry('900x680')
            path_var = tk.StringVar(value=get_global_reference_file() or "")
            top = tk.Frame(win, padx=10, pady=8); top.pack(fill='x')
            tk.Label(top, text='Path:').pack(side='left')
            ent = tk.Entry(top, textvariable=path_var, width=58); ent.pack(side='left', fill='x', expand=True, padx=(4,4))
            def browse():
                fname = filedialog.askopenfilename(parent=win)
                if fname: path_var.set(fname); _render()
            tk.Button(top, text='Browse', command=browse).pack(side='left')
            raw_mode = {'value': False}
            toggle_btn = tk.Button(top, text='Raw', width=5); toggle_btn.pack(side='left', padx=(6,0))
            copy_btn = tk.Button(top, text='Copy', width=6); copy_btn.pack(side='left', padx=(6,0))
            info = tk.Label(top, text=INFO_CLOSE_SAVE, fg='#555'); info.pack(side='left', padx=(12,0))
            frame = tk.Frame(win); frame.pack(fill='both', expand=True)
            txt = tk.Text(frame, wrap='word'); vs = tk.Scrollbar(frame, orient='vertical', command=txt.yview)
            txt.configure(yscrollcommand=vs.set); txt.pack(side='left', fill='both', expand=True); vs.pack(side='right', fill='y')
            SIZE_LIMIT = 200*1024
            def _apply_md(widget, content: str):
                import re
                lines = content.splitlines(); cursor=1; in_code=False; code_start=None
                for ln in lines:
                    idx=f'{cursor}.0'
                    if ln.strip().startswith('```'):
                        if not in_code:
                            in_code=True; code_start=idx
                        else:
                            try: widget.tag_add('codeblock', code_start, f'{cursor}.0 lineend')
                            except Exception: pass
                            in_code=False; code_start=None
                    cursor+=1
                full = widget.get('1.0','end-1c')
                for m in re.finditer(r'\*\*(.+?)\*\*', full): widget.tag_add('bold', f"1.0+{m.start(1)}c", f"1.0+{m.end(1)}c")
            def _render():
                txt.config(state='normal'); txt.delete('1.0','end')
                p = Path(path_var.get()).expanduser()
                if not p.exists(): txt.insert('1.0', '(No file selected)'); txt.config(state='disabled'); return
                try: content = read_file_safe(str(p)).replace('\r','')
                except Exception: content = '(Error reading file)'
                if len(content.encode('utf-8'))>SIZE_LIMIT:
                    content = '*** File truncated (too large) ***\n\n' + content[:SIZE_LIMIT//2]
                if not raw_mode['value']:
                    new=[]; in_code=False
                    for ln in content.splitlines():
                        if ln.strip().startswith('```'):
                            in_code = not in_code; new.append(ln); continue
                        if not in_code and ln.startswith('- '): ln = '• ' + ln[2:]
                        new.append(ln)
                    content_to_insert='\n'.join(new)
                else:
                    content_to_insert=content
                txt.insert('1.0', content_to_insert)
                if not raw_mode['value']:
                    try: _apply_md(txt, content_to_insert)
                    except Exception: pass
                txt.config(state='disabled')
            def _toggle():
                raw_mode['value'] = not raw_mode['value']; toggle_btn.configure(text=('MD' if raw_mode['value'] else 'Raw')); _render()
            def _copy():
                try: root.clipboard_clear(); root.clipboard_append(txt.get('1.0','end-1c'))
                except Exception: pass
            def _close():
                try:
                    ov = selector_service.load_overrides(); gfiles = ov.setdefault('global_files', {})
                    pv = path_var.get().strip()
                    if pv: gfiles['reference_file'] = pv
                    else: gfiles.pop('reference_file', None)
                    selector_service.save_overrides(ov)
                except Exception: pass
                win.destroy(); return 'break'
            toggle_btn.configure(command=_toggle)
            copy_btn.configure(command=_copy)
            win.bind('<Control-Return>', lambda e: _close())
            win.bind('<Escape>', lambda e: _close())
            win.protocol('WM_DELETE_WINDOW', lambda: _close())
            _render(); ent.focus_set()
        # Wrap global reference manager with visible error surfacing
        def _safe_open_global():
            try:
                _open_global_reference_manager()
            except Exception as e:
                try:
                    from tkinter import messagebox
                    messagebox.showerror('Global Reference', f'Failed: {e}')
                except Exception:
                    pass
        opt.add_command(label='Global reference file', command=_safe_open_global)
        def _reset_global():
            try: reset_global_reference_file()
            except Exception: pass
        opt.add_command(label='Reset global reference file', command=_reset_global)

    if extra_items:
        try:
            extra_items(opt, new_menubar)
        except Exception as e:  # pragma: no cover
            _log.error("extra_items hook failed: %s", e)

    new_menubar.add_cascade(label="Options", menu=opt)
    root.config(menu=new_menubar)
    return accelerators


__all__ = ["configure_options_menu"]
