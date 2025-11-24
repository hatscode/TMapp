# Secure Notes Application

## Overview
The Secure Notes Application is a cross-platform desktop note-taking application designed with a strong emphasis on security and privacy. It allows users to create, edit, and store notes securely, ensuring that sensitive information remains protected through encryption.

## Features
- **End-to-End Encryption**: All notes are encrypted before being saved, ensuring that only authorized users can access them.
- **User-Friendly Interface**: A simple and intuitive GUI for easy note management.
- **Cross-Platform Compatibility**: Runs on Windows, macOS, and Linux.
- **Secure Password Management**: Implements strong password policies and secure storage of credentials.
- **Privacy-Focused Design**: No user data is collected or transmitted, ensuring complete privacy.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/hatscode/secure-notes-app.git
   ```
2. Navigate to the project directory:
   ```
   cd secure-notes-app
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To start the application, run the following command:
```
python src/main.py
```

## Development
This project follows a security-first approach throughout its development. Comprehensive threat modeling has been conducted to identify potential vulnerabilities and mitigate risks. Contributions to enhance security features are welcome.

## Testing
Unit tests are provided to ensure the correctness and security of the encryption functionalities. To run the tests, use:
```
pytest tests/
```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.