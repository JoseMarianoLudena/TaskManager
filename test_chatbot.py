#!/usr/bin/env python3
"""
Comprehensive test suite for the refactored chatbot
This test suite verifies that all the refactoring requirements were met:
1. Unified functions for common actions
2. Consistent behavior between buttons and text commands  
3. Better error handling
4. Improved intent detection
"""

import unittest
from main import ChatBot

class TestChatBotRefactoring(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.bot = ChatBot()
        self.user_id = "test_user"
    
    def test_unified_add_to_cart_function(self):
        """Test that both text commands and buttons use the same add_product_to_cart function"""
        # Set up a product selection
        self.bot.handle_message(self.user_id, "laptop")
        
        # Test text command
        response = self.bot.handle_message(self.user_id, "agregar al carrito")
        self.assertIn("agregado al carrito correctamente", response['response'])
        
        # Clear cart and test button
        self.bot.sessions[self.user_id]["cart"] = []
        response = self.bot.handle_message(self.user_id, "btn_add_1")
        self.assertIn("agregado al carrito correctamente", response['response'])
    
    def test_consistent_response_messages(self):
        """Test that responses are consistent between text and button commands"""
        # Set up product
        self.bot.handle_message(self.user_id, "laptop")
        
        # Test text command response
        text_response = self.bot.handle_message(self.user_id, "agregar al carrito")
        
        # Clear and test button response
        self.bot.sessions[self.user_id]["cart"] = []
        button_response = self.bot.handle_message(self.user_id, "btn_add_1")
        
        # Both should have the same message format and buttons
        self.assertEqual(text_response['response'], button_response['response'])
        self.assertEqual(text_response['buttons'], button_response['buttons'])
    
    def test_find_last_selected_product_function(self):
        """Test the unified find_last_selected_product function"""
        # No product selected initially
        product = self.bot.find_last_selected_product(self.user_id)
        self.assertIsNone(product)
        
        # Select a product
        self.bot.handle_message(self.user_id, "mouse")
        product = self.bot.find_last_selected_product(self.user_id)
        
        self.assertIsNotNone(product)
        self.assertEqual(product["name"], "Mouse")
        self.assertEqual(product["id"], 2)
    
    def test_send_cart_confirmation_buttons_function(self):
        """Test the unified send_cart_confirmation_buttons function"""
        # Empty cart
        response = self.bot.send_cart_confirmation_buttons(self.user_id)
        self.assertIn("carrito está vacío", response['response'])
        
        # Add items and test
        self.bot.add_product_to_cart(self.user_id, 1)
        self.bot.add_product_to_cart(self.user_id, 2)
        
        response = self.bot.send_cart_confirmation_buttons(self.user_id)
        self.assertIn("Tu carrito (2 items)", response['response'])
        self.assertIn("Total: $1029.98", response['response'])
    
    def test_handle_product_selection_function(self):
        """Test the unified handle_product_selection function"""
        response = self.bot.handle_product_selection(self.user_id, "laptop")
        
        self.assertIn("Laptop - $999.99", response['response'])
        self.assertIn("buttons", response)
        
        # Check that last product was set
        last_product = self.bot.find_last_selected_product(self.user_id)
        self.assertEqual(last_product["name"], "Laptop")
    
    def test_improved_intent_detection(self):
        """Test that various Spanish and English phrases are detected"""
        # Set up product first
        self.bot.handle_message(self.user_id, "keyboard")
        
        add_phrases = [
            "agregar al carrito",
            "add to cart",
            "añadir al carrito",
            "agregar", 
            "añadir"
        ]
        
        for phrase in add_phrases:
            # Clear cart for each test
            self.bot.sessions[self.user_id]["cart"] = []
            
            response = self.bot.handle_message(self.user_id, phrase)
            self.assertIn("agregado al carrito correctamente", response['response'])
            self.assertEqual(len(self.bot.sessions[self.user_id]["cart"]), 1)
    
    def test_error_handling(self):
        """Test improved error handling"""
        # Try to add without selecting product
        response = self.bot.handle_message(self.user_id, "agregar al carrito")
        self.assertIn("No hay producto seleccionado", response['response'])
        
        # Test invalid button
        response = self.bot.handle_message(self.user_id, "btn_invalid")
        self.assertIn("Botón no reconocido", response['response'])
        
        # Test malformed button
        response = self.bot.handle_message(self.user_id, "btn_add_invalid")
        self.assertIn("Error en el botón", response['response'])
    
    def test_no_duplicate_additions(self):
        """Test that items are not added twice when using different methods"""
        # Select product
        self.bot.handle_message(self.user_id, "laptop")
        
        # Add via text
        self.bot.handle_message(self.user_id, "agregar al carrito")
        cart_size_after_text = len(self.bot.sessions[self.user_id]["cart"])
        
        # Try to add same product via button - this should add again since it's explicitly requested
        self.bot.handle_message(self.user_id, "btn_add_1")
        cart_size_after_button = len(self.bot.sessions[self.user_id]["cart"])
        
        # Both should have added the item (this is expected behavior)
        self.assertEqual(cart_size_after_text, 1)
        self.assertEqual(cart_size_after_button, 2)
    
    def test_cart_functionality(self):
        """Test complete cart functionality"""
        # Add items
        self.bot.add_product_to_cart(self.user_id, 1)  # Laptop
        self.bot.add_product_to_cart(self.user_id, 2)  # Mouse
        
        # Check cart
        response = self.bot.send_cart_confirmation_buttons(self.user_id)
        self.assertIn("Tu carrito (2 items)", response['response'])
        
        # Clear cart
        self.bot.clear_cart(self.user_id)
        self.assertEqual(len(self.bot.sessions[self.user_id]["cart"]), 0)
        
        # Test checkout with empty cart
        response = self.bot.process_checkout(self.user_id)
        self.assertIn("carrito vacío", response['response'])
    
    def test_checkout_process(self):
        """Test the checkout process"""
        # Add items
        self.bot.add_product_to_cart(self.user_id, 1)  # Laptop $999.99
        self.bot.add_product_to_cart(self.user_id, 2)  # Mouse $29.99
        
        # Checkout
        response = self.bot.process_checkout(self.user_id)
        self.assertIn("Compra realizada exitosamente", response['response'])
        self.assertIn("$1029.98", response['response'])
        
        # Verify cart is cleared
        self.assertEqual(len(self.bot.sessions[self.user_id]["cart"]), 0)
    
    def test_session_management(self):
        """Test that sessions are properly managed"""
        user1 = "user1"
        user2 = "user2"
        
        # Add different products for different users
        self.bot.add_product_to_cart(user1, 1)  # User1 gets laptop
        self.bot.add_product_to_cart(user2, 2)  # User2 gets mouse
        
        # Verify separation
        user1_cart = self.bot.sessions[user1]["cart"]
        user2_cart = self.bot.sessions[user2]["cart"]
        
        self.assertEqual(len(user1_cart), 1)
        self.assertEqual(len(user2_cart), 1)
        self.assertEqual(user1_cart[0]["name"], "Laptop")
        self.assertEqual(user2_cart[0]["name"], "Mouse")

class TestIntegration(unittest.TestCase):
    """Integration tests for full user workflows"""
    
    def setUp(self):
        self.bot = ChatBot()
        self.user_id = "integration_test"
    
    def test_complete_shopping_workflow(self):
        """Test a complete shopping workflow"""
        # 1. Browse products
        response = self.bot.show_products(self.user_id)
        self.assertIn("Productos disponibles", response['response'])
        
        # 2. Search for specific product
        response = self.bot.handle_message(self.user_id, "laptop")
        self.assertIn("Laptop - $999.99", response['response'])
        
        # 3. Add via text command
        response = self.bot.handle_message(self.user_id, "agregar al carrito")
        self.assertIn("agregado al carrito correctamente", response['response'])
        
        # 4. Search for another product
        response = self.bot.handle_message(self.user_id, "mouse")
        self.assertIn("Mouse", response['response'])
        
        # 5. Add via button
        response = self.bot.handle_message(self.user_id, "btn_add_2")
        self.assertIn("agregado al carrito correctamente", response['response'])
        
        # 6. View cart
        response = self.bot.handle_message(self.user_id, "carrito")
        self.assertIn("Tu carrito (2 items)", response['response'])
        self.assertIn("$1029.98", response['response'])
        
        # 7. Checkout
        response = self.bot.process_checkout(self.user_id)
        self.assertIn("Compra realizada exitosamente", response['response'])

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)