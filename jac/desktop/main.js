const { app, BrowserWindow, Tray, Menu, screen, ipcMain } = require('electron');
const path = require('path');

let win = null;
let tray = null;

function createWindow() {
  const { bounds } = screen.getPrimaryDisplay();
  win = new BrowserWindow({
    x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height,
    transparent: true,
    frame: false,
    hasShadow: false,
    resizable: false,
    movable: false,
    skipTaskbar: true,
    fullscreenable: false,
    alwaysOnTop: true,
    focusable: false,            // never steals focus from your work
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // float above normal windows; visible on every virtual desktop
  win.setAlwaysOnTop(true, 'screen-saver');
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  // start fully click-through; the overlay turns this off only while the
  // cursor is over the robot (so it never blocks your clicks elsewhere)
  win.setIgnoreMouseEvents(true, { forward: true });

  win.loadFile(path.join(__dirname, 'overlay.html'));
}

ipcMain.on('jac:click-through', (_e, ignore) => {
  if (win) win.setIgnoreMouseEvents(!!ignore, { forward: true });
});

function createTray() {
  tray = new Tray(path.join(__dirname, 'assets', 'tray.png'));
  tray.setToolTip('jac — hamroh');
  const menu = Menu.buildFromTemplate([
    { label: "Ko'rsatish / yashirish", click: () => { if (win) win.isVisible() ? win.hide() : win.show(); } },
    { type: 'separator' },
    { label: 'Chiqish', click: () => app.quit() },
  ]);
  tray.setContextMenu(menu);
}

app.whenReady().then(() => {
  createWindow();
  createTray();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

// keep running in the tray even if (somehow) windows close
app.on('window-all-closed', (e) => { /* stay alive in tray */ });
