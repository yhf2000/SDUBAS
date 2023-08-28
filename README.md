# SDUBAS-Backend: Blockchain-Based Academic System

This repository contains the backend code for SDUBAS, an academic system built on blockchain technology.

## Running Asynchronous Tasks

For each asynchronous task, use a separate terminal.

### Sending Email Verification Codes

To execute the asynchronous task for sending email verification codes, run the following command:

```bash
celery -A Celery.send_email worker --loglevel=INFO -P eventlet
```

### Performing Add Operations

To execute the asynchronous task for adding operations, run the following command:

```bash
celery -A Celery.add_operation worker --loglevel=INFO -P eventlet
```

## Encryption Methods

### Password Encryption

- Algorithm: SHA-256
- Salt: User's registration timestamp

### Operation Encryption

- Algorithm: SHA-256
- Output: Hexadecimal representation of the hash value

### Token Generation

- Generates a random UUID and returns its hexadecimal representation.

### Six-Digit Token (token_s6)

- Generates a six-digit random number.

Feel free to explore and contribute!
