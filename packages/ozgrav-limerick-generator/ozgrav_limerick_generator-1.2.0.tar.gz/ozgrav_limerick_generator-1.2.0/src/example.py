#!/usr/bin/env python3
"""
Example usage of the limerick_generator module.

This script demonstrates how to use the generate_limerick function
to create limericks about different topics.
"""

from .limerick_generator import generate_limerick


def main():
    """Demonstrate limerick generation with various topics and models."""

    print("=" * 40)
    print("🎭 Limerick Generator Examples 🎭")
    print("=" * 40)

    # Basic examples with default model
    try:
        print("\n🔹 Basic Example (using gpt-3.5-turbo):")
        print(f"\n📝 Topic: OzGrav")
        print("-" * 20)

        # Generate limerick for the topic
        limerick = generate_limerick("OzGrav")
        print(limerick)

    except Exception as e:
        print(f"❌ Error generating limerick for 'OzGrav': {e}")

    # Model comparison examples
    print("\n\n" + "=" * 40)
    print("🔹 Model Comparison Example:")

    try:
        print(f"\n🤖 Model: gpt-5-nano")
        print(f"📝 Topic: Gravitational Waves")
        print("-" * 30)

        limerick = generate_limerick("Gravitational Waves", model="gpt-5-nano")
        print(limerick)

    except Exception as e:
        print(f"❌ Error with model 'gpt-5-nano' for topic 'Gravitational Waves': {e}")

    # Output format examples
    print("\n\n" + "=" * 40)
    print("🔹 Output Format Examples:")

    demo_topic = "programming"

    try:
        print(f"\n📝 Topic: {demo_topic.title()} (JSON Output)")
        print("-" * 40)
        json_output = generate_limerick(demo_topic, output="json")
        print(json_output)

    except Exception as e:
        print(f"❌ Error generating output format examples: {e}")

    print("\n\n" + "=" * 40)
    print("✨ Interactive Custom Example:")

    # Interactive example with model and output format selection
    try:
        custom_topic = input("Enter a topic for your limerick: ").strip()
        if custom_topic:
            print("\nAvailable models:")
            print("1. gpt-3.5-turbo (fast, cost-effective)")
            print("2. gpt-4 (high quality, balanced)")
            print("3. gpt-5 (latest, most advanced)")
            print("4. gpt-5-mini (efficient, good quality)")
            print("5. gpt-5-nano (ultra-fast, lightweight)")

            model_choice = input(
                "Choose a model (1-5, or press Enter for default): "
            ).strip()

            model_map = {
                "1": "gpt-3.5-turbo",
                "2": "gpt-4",
                "3": "gpt-5",
                "4": "gpt-5-mini",
                "5": "gpt-5-nano",
            }

            selected_model = model_map.get(model_choice, "gpt-3.5-turbo")

            # Ask about output format
            print("\nOutput formats:")
            print("1. Text (just the limerick)")
            print("2. JSON (full OpenAI response)")
            print("3. YAML (full OpenAI response)")

            format_choice = input(
                "Choose output format (1-3, or press Enter for text): "
            ).strip()

            format_map = {"1": "text", "2": "json", "3": "yaml"}

            selected_format = format_map.get(format_choice, "text")
            format_descriptions = {"text": "Text", "json": "JSON", "yaml": "YAML"}
            format_type = format_descriptions[selected_format]

            print(f"\n🤖 Using model: {selected_model}")
            print(f"📝 Your limerick about '{custom_topic}' ({format_type} format):")
            print("-" * 50)

            result = generate_limerick(
                custom_topic, model=selected_model, output=selected_format
            )
            print(result)
        else:
            print("No topic provided, skipping custom example.")

    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
