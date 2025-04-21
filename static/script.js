document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages-container');
    const decryptKeyInput = document.getElementById('decrypt-key');
    const decryptButton = document.getElementById('decrypt-button');
    const decryptStatus = document.getElementById('decrypt-status');

    let encryptedMessagesData = null; // Store fetched encrypted data

    async function fetchMessages() {
        try {
            const response = await fetch('/messages');
            if (!response.ok) {
                // If not authenticated, the server might return 401 or redirect to login
                if (response.status === 401 || response.status === 403) {
                    messagesContainer.innerHTML = '<p>Please log in to view messages.</p>';
                    // Optionally redirect to login page: window.location.href = '/login';
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (!data || !data.data || !data.signature) {
                 messagesContainer.innerHTML = '<p>Invalid data format received from server.</p>';
                 console.error('Invalid data format:', data);
                 return;
            }

            encryptedMessagesData = data; // Store the encrypted data and signature
            displayEncryptedMessages(); // Display initial encrypted state

        } catch (error) {
            console.error('Error fetching messages:', error);
            messagesContainer.innerHTML = `<p style="color: red;">Error loading messages: ${error.message}</p>`;
        }
    }

    function displayEncryptedMessages() {
        messagesContainer.innerHTML = ''; // Clear previous messages

        if (!encryptedMessagesData || !encryptedMessagesData.data) {
             messagesContainer.innerHTML = '<p>No messages received yet or data is missing.</p>';
             return;
        }

        // Display a placeholder or encrypted indicator
        messagesContainer.innerHTML = '<p>Messages are encrypted. Enter key and click Decrypt.</p>';
        // We could also display the raw encrypted data here if desired
        // messagesContainer.innerHTML = `<p>Encrypted Data: ${encryptedMessagesData.data}</p>`;
    }


    function decryptMessages() {
        const key = decryptKeyInput.value;
        if (!key) {
            decryptStatus.textContent = 'Please enter a decryption key.';
            decryptStatus.style.color = 'orange';
            return;
        }

        if (!encryptedMessagesData || !encryptedMessagesData.data || !encryptedMessagesData.signature) {
             decryptStatus.textContent = 'No encrypted data available to decrypt.';
             decryptStatus.style.color = 'red';
             return;
        }

        decryptStatus.textContent = 'Decrypting...';
        decryptStatus.style.color = 'black';

        try {
            // Convert key to WordArray (CryptoJS requires this)
            // Assuming the key entered by the user is the raw key bytes represented as a string
            // In a real application, key derivation might be needed
            // For this example, we'll assume the user enters the key as a hex string or similar
            // A safer approach would be to derive the key from a user-provided passphrase
            // For simplicity, let's assume the user enters the key as a base64 string matching the server's AES_KEY
            // This is NOT secure for production, just for demonstration.
            // A better approach would be to use a passphrase and a key derivation function (KDF)
            // Let's assume the user enters the key as a simple string for now, and we'll hash it
            // This is still not ideal, but better than using a raw string directly.
            // For a proper AES-128 key, we need 16 bytes. Let's use SHA256 and take the first 16 bytes.
            const aesKey = CryptoJS.SHA256(key).toString(CryptoJS.enc.Hex).substring(0, 32); // Use first 16 bytes (32 hex chars)
            const hmacKey = CryptoJS.SHA256(key).toString(CryptoJS.enc.Hex); // Use full SHA256 hash for HMAC key

            const encryptedData = encryptedMessagesData.data;
            const signature = encryptedMessagesData.signature;

            // 1. HMAC Verification
            const hmacHash = CryptoJS.HmacSHA256(encryptedData, CryptoJS.enc.Hex.parse(hmacKey));
            const calculatedSignature = CryptoJS.enc.Base64.stringify(hmacHash);

            if (calculatedSignature !== signature) {
                decryptStatus.textContent = 'HMAC verification failed. Incorrect key or data tampered.';
                decryptStatus.style.color = 'red';
                messagesContainer.innerHTML = '<p style="color: red;">HMAC verification failed. Cannot decrypt.</p>';
                console.error('HMAC verification failed. Calculated:', calculatedSignature, 'Expected:', signature);
                return;
            }
            console.log('HMAC verification successful.');

            // 2. AES Decryption
            // The server sends IV + ciphertext base64 encoded.
            // We need to extract IV (first 16 bytes after base64 decode) and ciphertext.
            const decodedData = CryptoJS.enc.Base64.parse(encryptedData);
            const iv = CryptoJS.lib.WordArray.create(decodedData.words.slice(0, 4)); // First 16 bytes (4 words)
            const ciphertext = CryptoJS.lib.WordArray.create(decodedData.words.slice(4)); // Remaining words

            const decrypted = CryptoJS.AES.decrypt(
                { ciphertext: ciphertext },
                CryptoJS.enc.Hex.parse(aesKey),
                { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
            );

            const decryptedText = decrypted.toString(CryptoJS.enc.Utf8);

            // Attempt to parse as JSON
            let messages = [];
            try {
                messages = JSON.parse(decryptedText);
                if (!Array.isArray(messages)) {
                     throw new Error("Decrypted data is not a JSON array.");
                }
            } catch (parseError) {
                decryptStatus.textContent = 'Decryption successful, but failed to parse data as JSON.';
                decryptStatus.style.color = 'red';
                messagesContainer.innerHTML = `<p style="color: red;">Decryption successful, but invalid data format: ${parseError.message}</p><p>Raw decrypted text: ${decryptedText}</p>`;
                console.error('JSON parse error:', parseError, 'Decrypted text:', decryptedText);
                return;
            }


            decryptStatus.textContent = 'Decryption successful!';
            decryptStatus.style.color = 'green';

            // Store the key in sessionStorage on successful decryption
            sessionStorage.setItem('decryptionKey', key);

            // Display decrypted messages
            messagesContainer.innerHTML = ''; // Clear previous content

            if (messages.length === 0) {
                messagesContainer.innerHTML = '<p>No messages received yet.</p>';
                return;
            }

            messages.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message');

                messageElement.innerHTML = `
                    <div class="message-header">
                        <strong>From:</strong> ${message.from_number || 'N/A'}
                        <span class="timestamp"><strong>Received At:</strong> ${message.received_at || 'N/A'}</span>
                    </div>
                    <div class="message-content">
                        <strong>Content:</strong>
                        <div class="content-text">${message.content || 'N/A'}</div>
                    </div>
                `;

                // Add click listener to toggle details
                messageElement.addEventListener('click', () => {
                    const details = messageElement.querySelector('.message-details');
                    if (details.style.display === 'none') {
                        details.style.display = 'block';
                    } else {
                        details.style.display = 'none';
                    }
                });

                messagesContainer.appendChild(messageElement);
            });


        } catch (error) {
            decryptStatus.textContent = 'Decryption failed. Incorrect key or data corrupted.';
            decryptStatus.style.color = 'red';
            messagesContainer.innerHTML = `<p style="color: red;">Decryption failed: ${error.message}</p>`;
            console.error('Decryption error:', error);
        }
    }

    // Attach event listener to the decrypt button
    decryptButton.addEventListener('click', decryptMessages);

    // Fetch messages initially
    fetchMessages().then(() => {
        // After fetching, attempt to decrypt if a key is stored in sessionStorage
        const storedKey = sessionStorage.getItem('decryptionKey');
        if (storedKey) {
            decryptKeyInput.value = storedKey;
            decryptMessages(); // Automatically attempt decryption
        }
    });


    // Fetch messages every 5 seconds (will update encrypted data and re-attempt decryption if key is stored)
    setInterval(() => {
        fetchMessages().then(() => {
            const storedKey = sessionStorage.getItem('decryptionKey');
            if (storedKey && encryptedMessagesData) { // Only attempt if key is stored and we have data
                 decryptKeyInput.value = storedKey; // Ensure input field is populated
                 decryptMessages(); // Automatically attempt decryption with stored key
            }
        });
    }, 5000);
});
