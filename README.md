# Car Diagnosis Helper – Hello World Knowledge System

## Overview

This project is a small knowledge-based system that helps car owners reason about simple car problems based on
observable symptoms. The system asks a short series of questions and uses explicit rules to suggest likely causes and
possible next steps.

The goal is not to replace a professional mechanic, but to support car owners in understanding what might be wrong
before visiting a garage.

## Running the system

Requirements:

- Python 3.13 or higher

Steps:

1. Clone this repository.
2. In the project directory, run:

   ```bash
   python code/main.py
   ```

3. Answer the questions with `yes`, `no`, or press `Enter` to skip if you are unsure.
4. At the end, the system will display one or more possible issues and suggested next steps.

## Files

- main.py – entry point that starts an interactive diagnosis session.
- knowledge_base.py – definitions of symptoms and diagnostic rules.
- inference.py – simple inference engine that matches user answers to rules.
- requirements.txt – Python dependencies (none for this prototype).

## Limitations

This is an early prototype of a larger project. The rule base is very small and only
covers a few common situations one might encounter. The system should always be used
as a support tool, never as a replacement for professional advice.