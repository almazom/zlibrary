Feature: Confidence Validation System
  As a quality assurance system
  I want to validate book matches before EPUB delivery
  So that users only receive books they actually requested

  Background:
    Given I have authenticated Telegram user session "Клава Тех Поддержка"
    And the user session ID is "5282615364"
    And the target bot "@epub_toc_based_sample_bot" is accessible
    And MCP telegram-read-manager tool is available
    And the confidence validation system is operational

  Scenario: Reject wrong book with different author
    Given the bot is running and responsive
    And I have a book request for "Незападная история науки Джеймс Поскетт"
    When I send the book search request to the bot
    And the bot responds with "«Котлы» 41-го. История ВОВ, которую мы не знали"
    Then the confidence validation system should activate
    And it should parse user expected author as "Джеймс Поскетт"
    And it should detect no author match in bot response
    And it should calculate confidence score below 0.85
    And it should decline to deliver the EPUB
    And it should log the reason as "Wrong author - different book"
    And the test result should be marked as PASSED for correct rejection

  Scenario: Accept correct book with matching author
    Given the bot is running and responsive
    And I have a book request for "К себе нежно Ольга Примаченко"
    When I send the book search request to the bot
    And the bot responds with "К себе нежно. Книга о том, как ценить и беречь себя"
    Then the confidence validation system should activate
    And it should parse user expected author as "Ольга Примаченко"
    And it should find matching title content
    And it should calculate confidence score above 0.60
    And it should proceed with EPUB delivery
    And the test result should be marked as PASSED for correct acceptance

  Scenario: Atomic confidence validation testing
    Given I have confidence validation functions available
    When I test the exact failing scenario from production
    And I validate "Незападная история науки Джеймс Поскетт" against "«Котлы» 41-го. История ВОВ"
    Then the system should return confidence score below 0.85
    And the validation should return false (decline delivery)
    And the atomic test should PASS confirming correct rejection behavior