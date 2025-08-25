"""Authorization management view."""
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ..core.api_client import ApiClient
from .ui_components import async_operation, StatusButton, LoadingDialog


class AuthorizationView(ttk.Frame):
    """UI for managing OAuth authorizations."""
    
    def __init__(self, master, api: ApiClient, log: Callable[[str], None]):
        super().__init__(master)
        self.api = api
        self.log = log
        self._auth_auto_loaded = False  # Track if authorizations have been auto-loaded
        
        # Cache authentication state to avoid repeated API calls
        self._cached_auth_state = None
        self._last_auth_check = 0
        self._auth_cache_duration = 30  # 30 seconds
        
        self._setup_ui()

    def _setup_ui(self):
        # Control buttons
        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=(6, 4))
        
        self.refresh_btn = StatusButton(btns, text="Refresh Authorizations", command=self.refresh)
        self.refresh_btn.pack(side="left", padx=4)
        
        self.delete_btn = StatusButton(btns, text="Delete Selected", command=self.delete_selected)
        self.delete_btn.pack(side="left", padx=8)
        
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(btns, textvariable=self.status).pack(side="right")

        # Info label
        info_frame = ttk.Frame(self)
        info_frame.pack(fill="x", padx=4, pady=4)
        ttk.Label(info_frame, text="💡 Authorizations enable agents to access Google Drive, Sheets, etc.", 
                 foreground="gray").pack(anchor="w")

        # Authorization list
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)
        cols = ("id", "name")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="extended")
        
        for c, t, w in [
            ("id", "Authorization ID", 300),
            ("name", "Full Resource Name", 600),
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        
        # Event bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)
        self.tree.bind("<Button-3>", self._popup)
        
        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_selected)
        
        # Debouncing for button updates
        self._update_timer = None
        
        # Store full authorization data
        self._authorizations_data = {}
        
        # Cache selection state to avoid redundant tree.selection() calls
        self._cached_selection = None
        self._selection_is_dirty = True
        
        # Initialize button states without immediate API calls
        self._update_button_states()

    def _get_cached_auth_state(self) -> bool:
        """Get authentication state with local caching to reduce API calls."""
        now = time.time()
        
        # Use cached result if still fresh
        if (self._cached_auth_state is not None and 
            (now - self._last_auth_check) < self._auth_cache_duration):
            return self._cached_auth_state
        
        # Check authentication and cache result
        self._cached_auth_state = self.api.is_authenticated
        self._last_auth_check = now
        return self._cached_auth_state

    def _get_selection(self):
        """Get cached selection to avoid redundant tree.selection() calls."""
        if self._selection_is_dirty or self._cached_selection is None:
            self._cached_selection = self.tree.selection()
            self._selection_is_dirty = False
        return self._cached_selection

    def _update_button_states(self):
        """Update button states based on current conditions."""
        # Use cached authentication state to reduce API calls
        is_auth = self._get_cached_auth_state()
        self.refresh_btn.set_enabled(
            is_auth,
            "Authentication required" if not is_auth else ""
        )
        
        # Delete button - enabled only if authorizations are selected
        has_selection = bool(self._get_selection())
        self.delete_btn.set_enabled(
            has_selection,
            "Select authorizations to delete" if not has_selection else ""
        )

    def _on_selection_change(self, event=None):
        """Handle selection changes - IMMEDIATE update, no debouncing."""
        # Mark selection cache as dirty
        self._selection_is_dirty = True
        # Immediate update - no timers or delays
        self._update_button_states()

    def refresh(self):
        """Refresh the list of authorizations."""
        # Update button states immediately on click
        self._update_button_states()
        
        # Check authentication once at the start using cached state
        if not self._get_cached_auth_state():
            self.log("❌ Authentication required")
            return
            
        # Show loading dialog
        loading_dialog = LoadingDialog(self.winfo_toplevel(), "Loading authorizations...")
        self.refresh_btn.set_enabled(False, "Loading...")
        
        def callback(items):
            # Close loading dialog
            loading_dialog.close()
            self.refresh_btn.set_enabled(True)
            
            # Bulk delete all rows at once instead of one-by-one
            self.tree.delete(*self.tree.get_children())
            
            # Clear stored data
            self._authorizations_data.clear()
            
            if isinstance(items, Exception):
                self.log(f"❌ List error: {items}")
                self.status.set("Error")
                return
            
            # Use chunked filling for large datasets to avoid UI blocking
            self._fill_tree_chunked(items)
        
        async_operation(self.api.list_authorizations, callback=callback, ui_widget=self)

    def _fill_tree_chunked(self, rows, start=0, chunk=200):
        """Fill tree in chunks to avoid UI blocking with large datasets."""
        end = min(start + chunk, len(rows))
        for it in rows[start:end]:
            # Insert into tree
            item_id = self.tree.insert("", "end", values=(it["id"], it["name"]))
            # Store full data for future use
            self._authorizations_data[item_id] = it
        
        if end < len(rows):
            # Yield to UI thread, then continue with next chunk
            self.after(0, self._fill_tree_chunked, rows, end, chunk)
        else:
            # All done - update status and button states
            self.status.set(f"{len(rows)} authorization(s)")
            self._update_button_states()

    def delete_selected(self):
        """Delete selected authorizations."""
        # Use cached selection to avoid redundant tree.selection() call
        sel = self._get_selection()
        if not sel:
            messagebox.showinfo("No selection", "Select one or more authorizations to delete.")
            return
        
        # Get authorization IDs from stored data
        auth_ids = []
        for item_id in sel:
            if item_id in self._authorizations_data:
                auth_ids.append(self._authorizations_data[item_id]["id"])
        
        if not auth_ids:
            messagebox.showerror("Error", "Could not find authorization IDs for selected items.")
            return
        
        # Confirm deletion
        count = len(auth_ids)
        msg = f"Delete {count} authorization{'s' if count > 1 else ''}?\n\n"
        msg += "\n".join(f"• {auth_id}" for auth_id in auth_ids[:5])
        if count > 5:
            msg += f"\n... and {count - 5} more"
        
        if not messagebox.askyesno("Confirm deletion", msg):
            return
        
        self.log(f"🗑️ Deleting {count} authorization{'s' if count > 1 else ''}...")
        self.delete_btn.set_enabled(False, "Deleting...")
        
        def callback(results):
            self.delete_btn.set_enabled(True)
            
            if isinstance(results, Exception):
                self.log(f"❌ Delete error: {results}")
                return
            
            # Batch log messages to reduce UI spam
            ok = [k for k, (s, _) in results.items() if s == "deleted"]
            bad = {k: v for k, v in results.items() if v[0] != "deleted"}
            
            if ok:
                ok_display = ", ".join(ok[:10]) + ("…" if len(ok) > 10 else "")
                self.log(f"✅ Deleted {len(ok)} authorization(s): {ok_display}")
            
            # Show first 10 failures with details
            for k, (s, msg) in list(bad.items())[:10]:
                self.log(f"❌ {k}: {msg}")
            if len(bad) > 10:
                self.log(f"…and {len(bad)-10} more failures")
            
            self._update_button_states()
            # Auto-refresh to show updated list
            self.refresh()
        
        # Delete authorizations sequentially (to avoid API rate limits)
        def delete_multiple():
            results = {}
            for auth_id in auth_ids:
                try:
                    results[auth_id] = self.api.delete_authorization(auth_id)
                except Exception as e:
                    results[auth_id] = ("failed", str(e))
            return results
        
        async_operation(delete_multiple, callback=callback, ui_widget=self)

    def _popup(self, event):
        """Show context menu."""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def update_api(self, api: ApiClient):
        """Update the API client reference."""
        self.api = api
        # Clear cached auth state when API changes
        self._cached_auth_state = None
        self._last_auth_check = 0
        # Reset auto-load flag
        self._auth_auto_loaded = False
        # Update button states immediately
        self._update_button_states()
        
        # Auto-load authorizations if credentials are available and not loaded yet
        if self._get_cached_auth_state():
            self._auth_auto_loaded = True
            self.log("✅ Auto-loading authorizations...")
            # Use a small delay to ensure UI is ready
            self.after(50, self.refresh)

    def on_tab_selected(self):
        """Called when this tab is selected - trigger auto-loading if needed."""
        if not self._auth_auto_loaded and self._get_cached_auth_state():
            self._auth_auto_loaded = True
            self.log("✅ Auto-loading authorizations...")
            self.refresh()
