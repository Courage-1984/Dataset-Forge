#!/usr/bin/env python3
"""
Enhanced Emoji Utilities - Practical Examples

This script demonstrates the comprehensive emoji utilities features including:
- Emoji mapping and lookups
- Context-aware validation
- Smart suggestions
- Usage analysis
- Integration examples
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataset_forge.utils.emoji_utils import (
    get_emoji_handler,
    get_emoji_description_from_mapping,
    find_emoji_by_description,
    get_emoji_category,
    validate_emoji_appropriateness,
    suggest_appropriate_emojis,
    analyze_emoji_usage,
    extract_emojis
)
from dataset_forge.utils.printing import print_header, print_section, print_info, print_success, print_warning


def demo_basic_mapping():
    """Demonstrate basic emoji mapping functionality."""
    print_section("Basic Emoji Mapping")
    
    # Test emojis
    test_emojis = ["😀", "🎉", "🚀", "❤️", "📚", "🍕", "🎯", "✅", "⚠️", "💻"]
    
    for emoji in test_emojis:
        description = get_emoji_description_from_mapping(emoji)
        category = get_emoji_category(emoji)
        print_info(f"{emoji} -> {description} (category: {category})")


def demo_emoji_search():
    """Demonstrate emoji search by description."""
    print_section("Emoji Search by Description")
    
    # Search for different types of emojis
    search_terms = ["heart", "check", "star", "computer", "pizza", "car"]
    
    for term in search_terms:
        emojis = find_emoji_by_description(term)
        print_info(f"'{term}' emojis: {len(emojis)} found")
        if emojis:
            # Show first 5 results
            sample_emojis = emojis[:5]
            print_info(f"  Sample: {' '.join(sample_emojis)}")


def demo_context_validation():
    """Demonstrate context-aware appropriateness validation."""
    print_section("Context-Aware Appropriateness Validation")
    
    # Test different contexts
    contexts = [
        ("professional business meeting", "😀"),
        ("code review meeting", "💻"),
        ("classroom presentation", "📚"),
        ("casual social media", "🎉"),
        ("error report", "⚠️"),
        ("success celebration", "🎊")
    ]
    
    for context, emoji in contexts:
        validation = validate_emoji_appropriateness(emoji, context)
        status = "✅ Appropriate" if validation['is_appropriate'] else "❌ Inappropriate"
        print_info(f"Context: {context}")
        print_info(f"  Emoji: {emoji} -> {validation['description']}")
        print_info(f"  Status: {status}")
        print_info(f"  Category: {validation['category']}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print_warning(f"  Warning: {warning}")
        
        if validation['suggestions']:
            suggestions = validation['suggestions'][:3]  # Show first 3
            print_info(f"  Suggestions: {' '.join(suggestions)}")
        
        print()


def demo_smart_suggestions():
    """Demonstrate smart emoji suggestions."""
    print_section("Smart Emoji Suggestions")
    
    # Test different contexts
    suggestion_contexts = [
        ("success completion", "symbols"),
        ("error problem", "symbols"),
        ("love romance", "emotions"),
        ("food hungry", "food_drink"),
        ("travel vacation", "transport"),
        ("learning education", "objects")
    ]
    
    for context, category in suggestion_contexts:
        suggestions = suggest_appropriate_emojis(context, category)
        print_info(f"Context: '{context}' (category: {category})")
        print_info(f"  Suggestions: {' '.join(suggestions[:5])}")  # Show first 5
        print()


def demo_usage_analysis():
    """Demonstrate emoji usage analysis."""
    print_section("Emoji Usage Analysis")
    
    # Test different types of text
    test_texts = [
        "😀 😍 🎉 Great job! 🚀 💯 Keep up the amazing work! 🌟",
        "✅ Process completed successfully. 📊 Data analyzed. 🎯 Target achieved.",
        "😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀 😀",
        "No emojis in this text at all.",
        "💻 Code review complete! 🐛 Bug fixed! 🚀 Feature deployed! 🎉"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print_info(f"Text {i}: {text}")
        analysis = analyze_emoji_usage(text)
        
        print_info(f"  Total emojis: {analysis['total_emojis']}")
        print_info(f"  Unique emojis: {analysis['unique_emojis']}")
        print_info(f"  Categories: {analysis['categories']}")
        
        if analysis['most_used']:
            print_info(f"  Most used: {' '.join(analysis['most_used'][:3])}")
        
        if analysis['potential_issues']:
            for issue in analysis['potential_issues']:
                print_warning(f"  Issue: {issue}")
        
        if analysis['recommendations']:
            for rec in analysis['recommendations']:
                print_info(f"  Recommendation: {rec}")
        
        print()


def demo_menu_enhancement():
    """Demonstrate menu enhancement with appropriate emojis."""
    print_section("Menu Enhancement Example")
    
    # Create enhanced menu options
    success_emojis = suggest_appropriate_emojis("success completion")
    error_emojis = suggest_appropriate_emojis("error problem")
    info_emojis = suggest_appropriate_emojis("information help")
    process_emojis = suggest_appropriate_emojis("process workflow")
    
    enhanced_menu = {
        "1": (f"{success_emojis[0]} Process Complete", "process_complete_action"),
        "2": (f"{error_emojis[0]} Error Report", "error_report_action"),
        "3": (f"{info_emojis[0]} Help & Documentation", "help_action"),
        "4": (f"{process_emojis[0]} Workflow Management", "workflow_action"),
        "0": ("🚪 Exit", "exit_action"),
    }
    
    print_info("Enhanced Menu Options:")
    for key, (description, action) in enhanced_menu.items():
        print_info(f"  {key}. {description}")
    
    # Validate menu emojis
    print_info("\nMenu Emoji Validation:")
    for key, (description, action) in enhanced_menu.items():
        emojis = extract_emojis(description)
        for emoji in emojis:
            validation = validate_emoji_appropriateness(emoji, "menu interface")
            status = "✅" if validation['is_appropriate'] else "❌"
            print_info(f"  {status} {emoji} in '{description}' -> {validation['description']}")


def demo_file_categorization():
    """Demonstrate file type categorization with emojis."""
    print_section("File Type Categorization")
    
    # Sample file extensions
    file_extensions = ['.jpg', '.png', '.pdf', '.txt', '.py', '.js', '.mp3', '.mp4', '.zip', '.exe']
    
    def get_file_type_emoji(extension: str) -> str:
        """Get appropriate emoji for file type."""
        context_map = {
            '.jpg': 'image photo',
            '.png': 'image photo',
            '.pdf': 'document book',
            '.txt': 'document text',
            '.py': 'code programming',
            '.js': 'code programming',
            '.mp3': 'music audio',
            '.mp4': 'video movie',
            '.zip': 'archive compression',
            '.exe': 'application software'
        }
        
        context = context_map.get(extension.lower(), 'file document')
        suggestions = suggest_appropriate_emojis(context, "objects")
        return suggestions[0] if suggestions else "📄"
    
    print_info("File Type Emoji Mapping:")
    for ext in file_extensions:
        emoji = get_file_type_emoji(ext)
        category = get_emoji_category(emoji)
        description = get_emoji_description_from_mapping(emoji)
        print_info(f"  {ext} -> {emoji} ({description}, category: {category})")


def demo_user_feedback():
    """Demonstrate user feedback enhancement."""
    print_section("User Feedback Enhancement")
    
    def provide_feedback(message: str, feedback_type: str) -> str:
        """Provide user feedback with appropriate emojis."""
        context_map = {
            'success': 'success completion',
            'error': 'error problem',
            'warning': 'warning caution',
            'info': 'information help',
            'progress': 'progress loading'
        }
        
        context = context_map.get(feedback_type, 'information')
        suggestions = suggest_appropriate_emojis(context)
        emoji = suggestions[0] if suggestions else "ℹ️"
        
        return f"{emoji} {message}"
    
    # Test different feedback types
    feedback_examples = [
        ("Task completed successfully", "success"),
        ("An error occurred during processing", "error"),
        ("Please check your input data", "warning"),
        ("Processing your request", "progress"),
        ("Here's some helpful information", "info")
    ]
    
    print_info("Enhanced User Feedback:")
    for message, feedback_type in feedback_examples:
        enhanced_message = provide_feedback(message, feedback_type)
        print_info(f"  {enhanced_message}")


def demo_content_validation():
    """Demonstrate content validation for emoji usage."""
    print_section("Content Validation")
    
    def validate_content_emojis(content: str, context: str) -> dict:
        """Validate emoji usage in content for specific context."""
        emojis = extract_emojis(content)
        validation_results = []
        total_issues = 0
        
        for emoji in emojis:
            validation = validate_emoji_appropriateness(emoji, context)
            if validation['warnings']:
                total_issues += len(validation['warnings'])
            validation_results.append(validation)
        
        analysis = analyze_emoji_usage(content)
        
        return {
            'total_emojis': len(emojis),
            'total_issues': total_issues,
            'validation_results': validation_results,
            'analysis': analysis,
            'is_appropriate': total_issues == 0
        }
    
    # Test different content types
    content_examples = [
        ("😀 Great work on the project! 🎉", "professional business"),
        ("✅ Task completed successfully", "professional business"),
        ("🎉 🍕 🎊 Awesome party! 🎈 🎪", "casual social"),
        ("💻 Code review complete! 🐛 Bug fixed!", "technical development")
    ]
    
    print_info("Content Validation Results:")
    for content, context in content_examples:
        validation = validate_content_emojis(content, context)
        status = "✅ Appropriate" if validation['is_appropriate'] else "❌ Inappropriate"
        print_info(f"  Context: {context}")
        print_info(f"  Content: {content}")
        print_info(f"  Status: {status}")
        print_info(f"  Issues: {validation['total_issues']}")
        print_info(f"  Analysis: {validation['analysis']['total_emojis']} emojis, {validation['analysis']['unique_emojis']} unique")
        print()


def main():
    """Run all emoji utility demonstrations."""
    print_header("Enhanced Emoji Utilities - Comprehensive Demo")
    
    # Initialize emoji handler
    handler = get_emoji_handler()
    print_success(f"✅ Loaded {len(handler.emoji_mapping)} emoji mappings")
    print_success(f"✅ Available categories: {len(handler.emoji_categories)}")
    print()
    
    # Run all demonstrations
    demo_basic_mapping()
    demo_emoji_search()
    demo_context_validation()
    demo_smart_suggestions()
    demo_usage_analysis()
    demo_menu_enhancement()
    demo_file_categorization()
    demo_user_feedback()
    demo_content_validation()
    
    print_section("Demo Complete")
    print_success("🎉 All enhanced emoji utility features demonstrated successfully!")
    print_info("Use these utilities to enhance your Dataset Forge interfaces with appropriate, engaging, and accessible emoji usage.")


if __name__ == "__main__":
    main() 