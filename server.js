const express = require('express');
const app = express();
const path = require('path');

// Serve static files from the 'images' directory
app.use('/images', express.static(path.join(__dirname, 'images')));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
