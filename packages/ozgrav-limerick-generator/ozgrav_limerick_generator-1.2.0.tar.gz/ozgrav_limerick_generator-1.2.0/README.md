# Limerick Generator

A Python module that connects to OpenAI's ChatGPT API to generate limericks on any topic you specify.

## Features

- 🎭 Generate limericks on any topic
- 🤖 Multiple OpenAI model support (gpt-3.5-turbo, gpt-4, gpt-5, gpt-5-mini, gpt-5-nano)
- 📄 Multiple output formats (text, JSON, YAML) for accessing full OpenAI response data

## Installation

1. **Clone or download this repository**

2. **Install dependencies using poetry:**

   ```bash
   poetry install
   ```

3. **Set up your OpenAI API key:**

   You need an OpenAI API key to use this module. Get one from [OpenAI's website](https://platform.openai.com/api-keys).

   Set the API key as an environment variable:

   **On Linux/macOS:**

   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

   **On Windows:**

   ```cmd
   set OPENAI_API_KEY=your-api-key-here
   ```

   **Or add to your `.bashrc`/`.zshrc` for persistence:**

   ```bash
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

### Basic Usage

```python
from limerick_generator import generate_limerick

# Generate a limerick about cats (uses default gpt-3.5-turbo model)
limerick = generate_limerick("cats")
print(limerick)

# Generate a limerick using a specific model
limerick = generate_limerick("cats", model="gpt-4")
print(limerick)
```

### Example Output

```
There once was a cat from Peru,
Who dreamed of a mouse or two,
It pounced with great might,
Through day and through night,
But caught only dreams, it's true!
```

### Advanced Usage

```python
from limerick_generator import generate_limerick

# You can also pass the API key directly (not recommended for production)
limerick = generate_limerick("programming", api_key="your-api-key")
print(limerick)
```

## Running the Examples

Run the example script to see the module in action:

```bash
python example.py
```

This will generate limericks for several topics and allow you to enter a custom topic.

## API Reference

### `generate_limerick(topic, api_key=None, model="gpt-3.5-turbo", output="text")`

Generate a limerick about a specified topic using OpenAI's ChatGPT API.

**Parameters:**

- `topic` (str): The topic or theme for the limerick
- `api_key` (str, optional): OpenAI API key. If not provided, uses `OPENAI_API_KEY` environment variable
- `model` (str, optional): OpenAI model to use. Defaults to "gpt-3.5-turbo"
- `output` (str, optional): Output format. Defaults to "text"

**Supported Models:**

- `gpt-3.5-turbo` - Fast and cost-effective (default)
- `gpt-4` - High quality, balanced performance
- `gpt-5` - Latest and most advanced model
- `gpt-5-mini` - Efficient with good quality
- `gpt-5-nano` - Ultra-fast and lightweight


**Output Formats:**

- `text` - Returns just the limerick text (default)
- `json` - Returns the full OpenAI response as JSON string
- `yaml` - Returns the full OpenAI response as YAML string

**Returns:**

- `str`: A generated limerick about the specified topic (text), or the full OpenAI response in JSON/YAML format

**Raises:**

- `ValueError`: If no API key is provided, topic is invalid, or unsupported model/output is specified
- `Exception`: If there's an error communicating with the OpenAI API

## Model Selection Guide

Choose the right model for your needs:

- **gpt-3.5-turbo**: Best for general use, fastest response time, most cost-effective
- **gpt-4**: Higher quality output, better understanding of complex topics
- **gpt-5**: Latest model with advanced capabilities and improved creativity
- **gpt-5-mini**: Balanced option with good quality and efficiency
- **gpt-5-nano**: Optimized for speed with minimal resource usage

### Model Usage Examples

```python
# Using different models
limerick1 = generate_limerick("cats", model="gpt-3.5-turbo")  # Fast and economical
limerick2 = generate_limerick("quantum physics", model="gpt-4")  # Better for complex topics
limerick3 = generate_limerick("poetry", model="gpt-5")  # Most advanced creativity
limerick4 = generate_limerick("cooking", model="gpt-5-mini")  # Efficient quality
limerick5 = generate_limerick("weather", model="gpt-5-nano")  # Ultra-fast generation
```


### Output Format Examples

```python
# Default text output (just the limerick)
text_limerick = generate_limerick("cats", output="text")
print(text_limerick)

# JSON output (full OpenAI response)
json_response = generate_limerick("cats", output="json")
print(json_response)

# YAML output (full OpenAI response)
yaml_response = generate_limerick("cats", output="yaml")
print(yaml_response)

# Combine all parameters
full_example = generate_limerick(
    topic="programming",
    model="gpt-4",
    output="json"
)
print(full_example)
```

## Requirements

- Python 3.12+
- OpenAI Python library (>=1.0.0)
- Valid OpenAI API key

## Error Handling

The module includes comprehensive error handling for:

- Missing or invalid API keys
- Network connectivity issues
- Invalid input parameters
- OpenAI API errors

## Cost Considerations

This module supports multiple OpenAI models with different pricing tiers:

- **gpt-3.5-turbo**: Most cost-effective option
- **gpt-4**: Higher cost but better quality
- **gpt-5**: Premium pricing for latest capabilities
- **gpt-5-mini**: Balanced cost and performance
- **gpt-5-nano**: Optimized for cost efficiency

Each limerick generation costs a small amount based on OpenAI's pricing for the selected model. Monitor your usage through the OpenAI dashboard. Consider using gpt-3.5-turbo for high-volume applications or gpt-5 models when quality is paramount.

## Troubleshooting

### "OpenAI API key not found" Error

- Ensure you've set the `OPENAI_API_KEY` environment variable
- Verify the API key is valid and active
- Check that you have sufficient credits in your OpenAI account

### "Unsupported model" Error

- Check that you're using one of the supported models: gpt-3.5-turbo, gpt-4, gpt-5, gpt-5-mini, gpt-5-nano
- Verify the model name is spelled correctly (case-sensitive)
- Ensure your OpenAI account has access to the requested model

### "Error generating limerick" Error

- Check your internet connection
- Verify your OpenAI API key has the necessary permissions
- Ensure you haven't exceeded rate limits
- Try using a different model if one specific model is failing

## License

This project is open source. Feel free to modify and distribute as needed.
