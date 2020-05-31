const express = require('express');
const path = require('path');
const { spawn } = require('child_process');

const app = express();

app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 8080;

app.listen(PORT, () => console.log(`Server started on port ${PORT}...`));

// Python hardware control
const py = spawn('python3', ['py/controller.py']);
py.stdout.pipe(process.stdout);
py.stderr.pipe(process.stderr);

// const py = spawn('python3', ['py/controller.py'],
//     {stdio: [process.stdin, process.stdout, process.stderr]});

// Homepage route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'html', 'home.html'));
});

// Listen for Toggle LEDs button
app.post('/api/toggleLEDs', (req, res) => {
    py.stdin.write('toggle\n')
    res.sendStatus(200);
});

// Listen for Update LCD button
app.post('/api/updateLCD', (req, res) => {
    py.stdin.write('lcd\n');
    res.sendStatus(200);
});

// Listen for Shut Down button
app.post('/api/reboot', (req, res) => {
    spawn("sudo", ["reboot"]);
    res.sendStatus(200);
});
