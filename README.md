# Chainlit Bedrock Example

Fully integrated chainlit with bedrock

## Pre-requisites

- Python 3.12+
- AWS CLI with configured credentials

## Installation

1. install the package

```bash
pip install -r requirements.txt
```

## Setup env

1. copy [dev.env](env/dev.env) to `.env`

```bash
cp env/dev.env .env
```

1. edit `.env` and set the following variables, if necessary.

you can find all available model_id at [here](https://docs.anthropic.com/en/api/claude-on-amazon-bedrock)
```bash
MODEL_ID="anthropic.claude-3-haiku-20240307-v1:0"
```

## Usage

Run [Chainlit](https://github.com/Chainlit/chainlit) in watch mode

```bash
chainlit app.py -w
```
