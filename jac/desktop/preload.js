const { contextBridge, ipcRenderer } = require('electron');

// Minimal, safe bridge the overlay uses to toggle click-through:
// the robot asks the window to capture the mouse only while hovered.
contextBridge.exposeInMainWorld('jacAPI', {
  clickThrough: (ignore) => ipcRenderer.send('jac:click-through', ignore),
});
