import customtkinter
import sys
import re

class CTkScrollableDropdown(customtkinter.CTkToplevel):

    def __init__(self, attach, x=None, y=None, button_color=None, height: int = None, width: int = None,
                 fg_color=None, button_height: int = 20, justify="center", scrollbar_button_color=None,
                 scrollbar=True, scrollbar_button_hover_color=None, frame_border_width=0, values=[],
                 command=None, image_values=[], alpha: float = 0.95, frame_corner_radius=20, double_click=False,
                 frame_border_color=None, text_color=None, autocomplete=False,
                 hover_color=None, pagination: bool = True, items_per_page: int = 50,
                 groups=None, font=("Segoe UI", 12), fade_in_duration: bool = True, fps: int = 60, **button_kwargs):
        super().__init__(master=attach.winfo_toplevel(), takefocus=1)

        self.group_patterns = None
        self.grouped_values = None
        self.y_pos = None
        self.width_new = None
        self.x_pos = None
        self.focus()
        self.lift()
        self.alpha = alpha
        self.attach = attach
        self.corner = frame_corner_radius
        self.padding = 0
        self.focus_something = False
        self.disable = False
        self.update()
        self.old_kwargs = None
        self.widgets = {}
        self.all_values = values.copy()
        self.values = values.copy()
        self.hide_flag = True
        self.pagination = pagination
        self.items_per_page = items_per_page
        self.current_page = 0
        self.filtered_values = None
        self.current_group = 0
        self.font = font
        self.groups = []
        self.fade_enabled = fade_in_duration
        self.fps = max(1, int(fps))
        self.fade_animation_duration = 0.25
        self.animating = False

        if groups is not None:
            for g in groups:
                if isinstance(g, (list, tuple)) and len(g) >= 2:
                    self.groups.append({"name": g[0], "pattern": g[1]})
                else:
                    raise ValueError(f"groups must be a list of [name, pattern], got {g!r}")

        self.group_names = [g["name"] for g in self.groups]
        self.group_patterns = []
        included_values = set()

        for g in self.groups:
            pattern = g["pattern"]
            if pattern == "__OTHERS__":
                self.group_patterns.append("__OTHERS__")
            else:
                compiled = re.compile(pattern)
                self.group_patterns.append(compiled)
                matched = [v for v in self.all_values if compiled.search(v)]
                included_values.update(matched)

        self.grouped_values = {}
        for i, pat in enumerate(self.group_patterns):
            if pat == "__OTHERS__":
                self.grouped_values[i] = [v for v in self.all_values if v not in included_values]
            else:
                self.grouped_values[i] = [v for v in self.all_values if pat.search(v)]

        if sys.platform.startswith("win"):
            self.after(100, lambda: self.overrideredirect(True))
            self.transparent_color = self._apply_appearance_mode(self._fg_color) if hasattr(self, '_fg_color') else "#FFFFFF"
            self.attributes("-transparentcolor", self.transparent_color)
        elif sys.platform.startswith("darwin"):
            self.overrideredirect(True)
            self.transparent_color = 'systemTransparent'
            self.attributes("-transparent", True)
            self.focus_something = True
        else:
            self.overrideredirect(True)
            self.transparent_color = '#000001'
            self.corner = 0
            self.padding = 18
            self.withdraw()
        self.hide_flag = True
        self.attach.bind('<Configure>', lambda e: self._withdraw() if not self.disable else None, add="+")
        self.attach.winfo_toplevel().bind('<Configure>', lambda e: self._withdraw() if not self.disable else None, add="+")
        self.attach.winfo_toplevel().bind("<ButtonPress>", lambda e: self._withdraw() if not self.disable else None, add="+")
        self.bind("<Escape>", lambda e: self._withdraw() if not self.disable else None, add="+")
        self.attributes('-alpha', 0)
        self.fg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"] if fg_color is None else fg_color
        self.scroll_button_color = customtkinter.ThemeManager.theme["CTkScrollbar"]["button_color"] if scrollbar_button_color is None else scrollbar_button_color
        self.scroll_hover_color = customtkinter.ThemeManager.theme["CTkScrollbar"]["button_hover_color"] if scrollbar_button_hover_color is None else scrollbar_button_hover_color
        self.frame_border_color = customtkinter.ThemeManager.theme["CTkFrame"]["border_color"] if frame_border_color is None else frame_border_color
        self.button_color = customtkinter.ThemeManager.theme["CTkButton"]["fg_color"] if button_color is None else button_color
        self.text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color
        self.hover_color = customtkinter.ThemeManager.theme["CTkButton"]["hover_color"] if hover_color is None else hover_color
        if not scrollbar:
            self.scroll_button_color = self.fg_color
            self.scroll_hover_color = self.fg_color
        if self.pagination:
            self.search_var = customtkinter.StringVar()
            self.search_var.trace_add('write', lambda *args: self.live_update(self.search_var.get()))
            self.search_entry = customtkinter.CTkEntry(self, textvariable=self.search_var)
            self.search_entry.pack(fill="x", pady=(0, 5))
        if self.groups:
            self.group_frame = customtkinter.CTkFrame(self, fg_color=self.fg_color, bg_color=self.transparent_color)
            self.group_frame.pack(fill="x", padx=5, pady=(0, 5))
            self.group_buttons = []
            for idx, name in enumerate(self.group_names):
                btn = customtkinter.CTkButton(
                    self.group_frame,
                    text=name,
                    font=self.font,
                    height=button_height,
                    fg_color=self.button_color,
                    text_color=self.text_color,
                    hover_color=self.hover_color,
                    command=lambda i=idx: self.switch_group(i),
                )
                self.group_buttons.append(btn)
            self.group_frame.bind("<Configure>", self._on_group_frame_configure, add="+")
            self.group_button_colors = [btn.cget("fg_color") for btn in self.group_buttons]
        self.frame = customtkinter.CTkScrollableFrame(
            self,
            bg_color=self.transparent_color,
            fg_color=self.fg_color,
            scrollbar_button_hover_color=self.scroll_hover_color,
            corner_radius=self.corner,
            border_width=frame_border_width,
            scrollbar_button_color=self.scroll_button_color,
            border_color=self.frame_border_color
        )
        self.frame._scrollbar.grid_configure(padx=3)
        self.frame.pack(expand=True, fill="both", pady=(3, 0))
        if self.pagination:
            self.button_container = customtkinter.CTkFrame(self.frame, fg_color=self.fg_color)
            self.button_container.pack(expand=True, fill="both")
            self.pagination_frame = customtkinter.CTkFrame(self.frame, fg_color=self.fg_color)
            self.pagination_frame.pack(fill="x", side="bottom")
        else:
            self.button_container = self.frame
        self.dummy_entry = customtkinter.CTkEntry(self.frame, fg_color="transparent", border_width=0, height=1, width=1)
        self.is_height = bool(height)
        if height is None:
            self.height_new = attach.winfo_toplevel().winfo_height()
        else:
            self.height_new = height
        self.width = width
        self.command = command
        self.fade = False
        self.autocomplete = autocomplete
        self.var_update = customtkinter.StringVar()
        self.appear = True
        if justify.lower() == "left":
            self.justify = "w"
        elif justify.lower() == "right":
            self.justify = "e"
        else:
            self.justify = "c"
        self.button_height = button_height
        self.image_values = image_values
        self.value_to_image = {}
        if image_values and len(image_values) == len(values):
            for val, img in zip(values, image_values):
                self.value_to_image[val] = img
        self.resizable(width=False, height=False)
        self.transient(self.master)
        if double_click or isinstance(self.attach, customtkinter.CTkEntry) or isinstance(self.attach, customtkinter.CTkComboBox):
            self.attach.bind('<Double-Button-1>', lambda e: self._iconify(), add="+")
        else:
            self.attach.bind('<Button-1>', lambda e: self._iconify(), add="+")
        if isinstance(self.attach, customtkinter.CTkComboBox):
            self.attach._canvas.tag_bind("right_parts", "<Button-1>", lambda e: self._iconify())
            self.attach._canvas.tag_bind("dropdown_arrow", "<Button-1>", lambda e: self._iconify())
            if self.command is None:
                self.command = self.attach.set
        if isinstance(self.attach, customtkinter.CTkOptionMenu):
            self.attach._canvas.bind("<Button-1>", lambda e: self._iconify())
            self.attach._text_label.bind("<Button-1>", lambda e: self._iconify())
            if self.command is None:
                self.command = self.attach.set
        self.attach.bind("<Destroy>", lambda _: self._destroy(), add="+")
        self.update_idletasks()
        self.x = x
        self.y = y
        if self.autocomplete:
            self.bind_autocomplete()
        self.withdraw()
        self.attributes("-alpha", 0)
        if self.groups:
            self.switch_group(0)
        self._init_buttons()

    def _on_group_frame_configure(self, event):
        if not self.group_buttons:
            return

        min_btn_width = 100
        n = len(self.group_buttons)
        cols = max(1, min(n, event.width // min_btn_width))
        rows = (n + cols - 1) // cols

        frame_height = rows * self.button_height
        if self.group_frame.winfo_height() != frame_height:
            self.group_frame.configure(height=frame_height)

        for idx, btn in enumerate(self.group_buttons):
            row = idx // cols
            col_in_row = idx % cols
            row_start = row * cols
            num_in_row = min(cols, n - row_start)

            rel_width = 1.0 / num_in_row
            rel_x = col_in_row * rel_width
            rel_y = row / rows
            rel_height = 1.0 / rows

            btn.place(
                in_=self.group_frame,
                relx=rel_x,
                rely=rel_y,
                relwidth=rel_width,
                relheight=rel_height
            )

    def switch_group(self, idx):
        if idx == self.current_group:
            self.values = self.all_values.copy()
            self.current_group = None
        else:
            self.current_group = idx
            self.values = self.grouped_values[idx].copy()
        for i, btn in enumerate(self.group_buttons):
            if i == self.current_group:
                btn.configure(fg_color=self.hover_color)
            else:
                btn.configure(fg_color=self.group_button_colors[i])
        self.filtered_values = None
        self.current_page = 0
        self._init_buttons()

    def update_buttons(self, values_list):
        for i, value in enumerate(values_list):
            if i in self.widgets:
                btn, _ = self.widgets[i]
                btn.configure(text=value, command=lambda v=value: self._attach_key_press(v), image=self.value_to_image.get(value))
                btn.pack(fill="x", pady=2, padx=(self.padding, 0))
                self.widgets[i][1] = True
            else:
                btn = customtkinter.CTkButton(
                    self.button_container,
                    text=value,
                    font=self.font,
                    command=lambda v=value: self._attach_key_press(v),
                    height=self.button_height,
                    fg_color=self.button_color,
                    text_color=self.text_color,
                    anchor=self.justify,
                    hover_color=self.hover_color,
                    image=self.value_to_image.get(value)
                )
                btn.pack(fill="x", pady=2, padx=(self.padding, 0))
                self.widgets[i] = [btn, True]
        i = len(values_list)
        while i in self.widgets:
            btn, visible = self.widgets[i]
            if visible:
                btn.pack_forget()
                self.widgets[i][1] = False
            i += 1

    def _destroy(self):
        self.after(500, self.destroy_popup)

    def _withdraw(self):
        if self.animating:
            return
        if not self.winfo_exists():
            return
        if self.winfo_viewable() and self.hide_flag:
            self._animated_withdraw()
            return
        self.event_generate("<<Closed>>")
        self.hide_flag = True

    def _update(self, a, b, c):
        self.live_update(self.attach._entry.get())

    def bind_autocomplete(self):
        def appear(x):
            self.appear = True
        if isinstance(self.attach, customtkinter.CTkComboBox):
            self.attach._entry.configure(textvariable=self.var_update)
            self.attach._entry.bind("<Key>", appear)
            if self.values:
                self.attach.set(self.values[0])
            self.var_update.trace_add('write', self._update)
        if isinstance(self.attach, customtkinter.CTkEntry):
            self.attach.configure(textvariable=self.var_update)
            self.attach.bind("<Key>", appear)
            self.var_update.trace_add('write', self._update)

    def _init_buttons(self):
        if self.pagination:
            values_to_show = self.values[self.current_page * self.items_per_page:
                                         (self.current_page + 1) * self.items_per_page]
            self._update_pagination_buttons()
        else:
            values_to_show = self.values
        self.update_buttons(values_to_show)
        self.frame._parent_canvas.yview_moveto(0)

    def _update_pagination_buttons(self, filtered=False):
        if not self.pagination:
            return
        for child in self.pagination_frame.winfo_children():
            child.destroy()
        values_list = self.filtered_values if (filtered and self.filtered_values is not None) else self.values
        total_pages = (len(values_list) + self.items_per_page - 1) // self.items_per_page
        button_width = 30
        button_padding = 4
        available_width = self.pagination_frame.winfo_width() if self.pagination_frame.winfo_ismapped() else self.width_new
        if available_width < 1:
            available_width = self.attach.winfo_width() if self.width is None else self.width
        max_buttons_per_row = max(1, available_width // (button_width + button_padding))
        total_rows = (total_pages + max_buttons_per_row - 1) // max_buttons_per_row
        for row in range(total_rows):
            for col in range(max_buttons_per_row):
                page_index = row * max_buttons_per_row + col
                if page_index >= total_pages:
                    break
                state = "disabled" if page_index == self.current_page else "normal"
                btn = customtkinter.CTkButton(
                    self.pagination_frame,
                    text=str(page_index + 1),
                    width=button_width,
                    height=30,
                    fg_color=self.button_color,
                    text_color=self.text_color,
                    command=lambda p=page_index: self._change_page(p),
                    state=state
                )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        for col in range(max_buttons_per_row):
            self.pagination_frame.grid_columnconfigure(col, weight=1)

    def _change_page(self, page_index):
        self.current_page = page_index
        if self.filtered_values is not None:
            values_to_show = self.filtered_values[self.current_page * self.items_per_page:
                                                  (self.current_page + 1) * self.items_per_page]
        else:
            values_to_show = self.values[self.current_page * self.items_per_page:
                                         (self.current_page + 1) * self.items_per_page]
            self.update_buttons(values_to_show)
            self._update_pagination_buttons(filtered=bool(self.filtered_values))
            self.frame.update_idletasks()
            self.frame._parent_canvas.yview_moveto(len(values_to_show) / self.items_per_page)

    def destroy_popup(self):
        self.destroy()
        self.disable = True

    def place_dropdown(self):
        if not self.winfo_exists():
            return
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        current_x_pos = self.winfo_x()
        current_y_pos = self.winfo_y()
        self.x_pos = self.attach.winfo_rootx() if self.x is None else self.x + self.attach.winfo_rootx()
        self.width_new = self.attach.winfo_width() if self.width is None else self.width
        if not self.is_height:
            self.height_new = self.attach.winfo_toplevel().winfo_height()
        screen_height = self.winfo_screenheight()
        dropdown_bottom = self.attach.winfo_rooty() + self.height_new
        if dropdown_bottom > screen_height:
            self.y_pos = max(0, self.attach.winfo_rooty() - self.height_new)
        else:
            self.y_pos = self.attach.winfo_rooty() + self.attach.winfo_height()
        if (current_width != self.width_new
                or current_height != self.height_new
                or current_x_pos != self.x_pos
                or current_y_pos != self.y_pos):
            self.geometry(f"{self.width_new}x{self.height_new}+{self.x_pos}+{self.y_pos}")
            if self.fade_enabled:
                self.attributes('-alpha', 0)
            else:
                self.attributes('-alpha', self.alpha)
            self.update_idletasks()
            if self.pagination:
                self._update_pagination_buttons(filtered=bool(self.filtered_values))

    def _iconify(self):
        if self.animating:
            return
        if self.attach.cget("state") == "disabled":
            return
        if self.disable:
            return
        if self.winfo_ismapped():
            self.hide_flag = False
        if self.hide_flag and self.all_values:
            self.event_generate("<<Opened>>")
            self.focus()
            self.hide_flag = False
            self.place_dropdown()
            self._deiconify()
        else:
            self._animated_withdraw()
            self.hide_flag = True

    def _attach_key_press(self, k):
        if self.animating:
            return
        if hasattr(self, "search_var"):
            self.search_var.set("")
        self.event_generate("<<Selected>>")
        self.fade = True
        if self.command:
            self.command(k)
        if hasattr(self, "search_var") and self.search_var.get().strip() != "":
            self.filtered_values = None
            self.current_page = 0
            self._init_buttons()
            if self.pagination:
                self.pagination_frame.pack(fill="x", side="bottom")
        self.fade = False
        self._animated_withdraw()
        self.hide_flag = True

    def live_update(self, string=None):
        if self.disable or self.fade or self.animating:
            return
        self.frame._parent_canvas.yview_moveto(0)
        if string and string.strip() != "":
            string = string.lower()
            filtered = [val for val in self.values if string in val.lower()]
            self.filtered_values = filtered
            if self.pagination:
                total_pages = (len(filtered) + self.items_per_page - 1) // self.items_per_page
                if self.current_page >= total_pages:
                    self.current_page = 0
                self._update_pagination_buttons(filtered=True)
                values_to_show = filtered[self.current_page * self.items_per_page:(self.current_page + 1) * self.items_per_page]
            else:
                values_to_show = filtered
            self.update_buttons(values_to_show)
            if self.pagination:
                self.pagination_frame.pack(fill="x", side="bottom")
            self.place_dropdown()
        else:
            if self.pagination:
                self.pagination_frame.pack(fill="x", side="bottom")
            self.filtered_values = None
            self.current_page = 0
            self._init_buttons()
            self.place_dropdown()
            self.appear = False

    def insert(self, value, **kwargs):
        index = len(self.values)
        if index in self.widgets:
            btn, _ = self.widgets[index]
            btn.configure(text=value, command=lambda v=value: self._attach_key_press(v), image=self.value_to_image.get(value))
            btn.pack(fill="x", pady=2, padx=(self.padding, 0))
            self.widgets[index][1] = True
        else:
            btn = customtkinter.CTkButton(self.button_container,
                                          text=value,
                                          height=self.button_height,
                                          fg_color=self.button_color,
                                          text_color=self.text_color,
                                          hover_color=self.hover_color,
                                          anchor=self.justify,
                                          command=lambda v=value: self._attach_key_press(v),
                                          image=self.value_to_image.get(value),
                                          width=0,
                                          *kwargs)
            btn.pack(fill="x", pady=2, padx=(self.padding, 0))
            self.widgets[index] = [btn, True]
        self.values.append(value)
        self.all_values.append(value)
        if self.groups:
            self.grouped_values[self.current_group].append(value)
        if self.pagination:
            self._update_pagination_buttons()

    def _deiconify(self):
        if self.all_values:
            if self.fade_enabled:
                if self.animating:
                    return
                self.deiconify()
                self._animate_fade_in()
            else:
                self.deiconify()
                self.attributes('-alpha', self.alpha)

    def popup(self, x=None, y=None):
        self.x = x
        self.y = y
        self.hide_flag = True
        self._iconify()

    def hide(self):
        self._withdraw()

    def configure(self, **kwargs):
        if self.old_kwargs == kwargs:
            return
        if "height" in kwargs:
            self.height_new = kwargs.pop("height")
        if "alpha" in kwargs:
            self.alpha = kwargs.pop("alpha")
        if "width" in kwargs:
            self.width = kwargs.pop("width")
        if "fg_color" in kwargs:
            self.frame.configure(fg_color=kwargs.pop("fg_color"))
        if "values" in kwargs:
            self.all_values = kwargs.pop("values")
            self.values = self.all_values.copy()
            self.image_values = None
            self.current_page = 0
            self._init_buttons()
            if hasattr(self, "search_var"):
                self.search_var.set("")
            if getattr(self, "groups", None):
                self.group_patterns = []
                included_values = set()
                for g in self.groups:
                    pattern = g["pattern"]
                    if pattern == "__OTHERS__":
                        self.group_patterns.append("__OTHERS__")
                    else:
                        compiled = re.compile(pattern)
                        self.group_patterns.append(compiled)
                        matched = [v for v in self.all_values if compiled.search(v)]
                        included_values.update(matched)
                self.grouped_values = {}
                for i, pat in enumerate(self.group_patterns):
                    if pat == "__OTHERS__":
                        self.grouped_values[i] = [v for v in self.all_values if v not in included_values]
                    else:
                        self.grouped_values[i] = [v for v in self.all_values if pat.search(v)]
                self.switch_group(self.current_group)
        if "groups" in kwargs:
            raw_groups = kwargs.pop("groups")
            self.groups = []
            for g in raw_groups:
                if isinstance(g, (list, tuple)) and len(g) >= 2:
                    self.groups.append({"name": g[0], "pattern": g[1]})
                else:
                    raise ValueError(f"groups must be list of [name, pattern], got {g!r}")

            self.group_names = [g["name"] for g in self.groups]
            self.group_patterns = []
            included_values = set()

            for g in self.groups:
                pattern = g["pattern"]
                if pattern == "__OTHERS__":
                    self.group_patterns.append("__OTHERS__")
                else:
                    compiled = re.compile(pattern)
                    self.group_patterns.append(compiled)
                    matched = [v for v in self.all_values if compiled.search(v)]
                    included_values.update(matched)

            self.grouped_values = {}
            for i, pat in enumerate(self.group_patterns):
                if pat == "__OTHERS__":
                    self.grouped_values[i] = [v for v in self.all_values if v not in included_values]
                else:
                    self.grouped_values[i] = [v for v in self.all_values if pat.search(v)]

            self.current_group = 0
            self.switch_group(self.current_group)
        if "image_values" in kwargs:
            image_values_arg = kwargs.pop("image_values")
            self.image_values = image_values_arg
            self.value_to_image = {}

            if image_values_arg and len(image_values_arg) == len(self.values):
                for val, img in zip(self.values, image_values_arg):
                    self.value_to_image[val] = img

            for key, (btn, visible) in self.widgets.items():
                current_value = btn.cget("text")
                btn.configure(image=self.value_to_image.get(current_value))
        if "button_color" in kwargs:
            bc = kwargs.pop("button_color")
            for key in self.widgets:
                self.widgets[key][0].configure(fg_color=bc)
        if self.old_kwargs != kwargs:
            for key in self.widgets:
                self.widgets[key][0].configure(**kwargs)
        self.old_kwargs = kwargs
        self.master.update()

    def _animate_fade_in(self):
        if not self.fade_enabled:
            self.attributes('-alpha', self.alpha)
            return
        if self.animating:
            return
        self.animating = True
        total_frames = max(1, int(self.fps * self.fade_animation_duration))
        step = float(self.alpha) / total_frames
        current = 0.0
        interval = max(1, int(1000 / self.fps))
        def step_fn(frame, value):
            new_value = value + step
            if new_value >= self.alpha or frame >= total_frames - 1:
                try:
                    self.attributes('-alpha', self.alpha)
                finally:
                    self.animating = False
                return
            try:
                self.attributes('-alpha', new_value)
            except Exception:
                pass
            self.after(interval, lambda: step_fn(frame + 1, new_value))
        try:
            self.attributes('-alpha', 0.0)
        except Exception:
            pass
        step_fn(0, current)

    def _animated_withdraw(self):
        if not self.winfo_exists():
            return
        if not self.fade_enabled:
            if self.winfo_viewable():
                self.withdraw()
            self.event_generate("<<Closed>>")
            self.hide_flag = True
            return
        if self.animating:
            return
        self.animating = True
        total_frames = max(1, int(self.fps * self.fade_animation_duration))
        step = float(self.alpha) / total_frames
        interval = max(1, int(1000 / self.fps))
        current_alpha = None
        try:
            current_alpha = float(self.attributes('-alpha'))
        except Exception:
            current_alpha = self.alpha
        def step_fn(frame, value):
            new_value = value - step
            if new_value <= 0 or frame >= total_frames - 1:
                try:
                    self.attributes('-alpha', 0.0)
                finally:
                    try:
                        if self.winfo_viewable():
                            self.withdraw()
                    finally:
                        self.event_generate("<<Closed>>")
                        self.hide_flag = True
                        self.animating = False
                return
            try:
                self.attributes('-alpha', new_value)
            except Exception:
                pass
            self.after(interval, lambda: step_fn(frame + 1, new_value))
        step_fn(0, current_alpha)
