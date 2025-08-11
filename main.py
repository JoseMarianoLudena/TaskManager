#!/usr/bin/env python3
"""
Refactored Chatbot with unified cart logic - AFTER refactoring
This file fixes the problems described in the issue:
1. Unified functions for common actions
2. Consistent behavior between buttons and text commands
3. Better code organization
4. Improved maintainability and error handling
"""

import json
import re
from typing import Dict, List, Optional, Any

# Product catalog (moved to better organization)
AVAILABLE_PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Mouse", "price": 29.99},
    {"id": 3, "name": "Keyboard", "price": 79.99},
    {"id": 4, "name": "Monitor", "price": 299.99}
]

class ChatBot:
    def __init__(self):
        self.sessions = {}
        
    def _get_or_create_session(self, user_id: str) -> Dict[str, Any]:
        """Get or create user session"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "cart": [],
                "last_product": None,
                "state": "browsing"
            }
        return self.sessions[user_id]
    
    def handle_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Main message handler with unified logic"""
        session = self._get_or_create_session(user_id)
        message_lower = message.lower().strip()
        
        # Handle button presses
        if message.startswith("btn_"):
            return self.handle_button_press(user_id, message)
        
        # Handle add to cart text commands - NOW UNIFIED
        if self._is_add_to_cart_intent(message_lower):
            return self.add_product_to_cart(user_id)
        
        # Handle product search
        if self._is_product_search(message_lower):
            return self.handle_product_selection(user_id, message_lower)
        
        # Handle cart viewing
        if self._is_view_cart_intent(message_lower):
            return self.send_cart_confirmation_buttons(user_id)
            
        return {"response": "No entiendo. ¿Puedes ser más específico?"}
    
    def _is_add_to_cart_intent(self, message: str) -> bool:
        """Unified intent detection for add to cart"""
        add_patterns = [
            "agregar al carrito",
            "add to cart", 
            "añadir al carrito",
            "agregar",
            "añadir"
        ]
        return any(pattern in message for pattern in add_patterns)
    
    def _is_product_search(self, message: str) -> bool:
        """Check if message is a product search"""
        product_names = [product["name"].lower() for product in AVAILABLE_PRODUCTS]
        return any(name in message for name in product_names)
    
    def _is_view_cart_intent(self, message: str) -> bool:
        """Check if message is requesting to view cart"""
        cart_patterns = ["carrito", "cart", "ver carrito", "view cart"]
        return any(pattern in message for pattern in cart_patterns)
    
    def find_last_selected_product(self, user_id: str) -> Optional[Dict[str, Any]]:
        """UNIFIED: Find the last selected product"""
        session = self._get_or_create_session(user_id)
        return session.get("last_product")
    
    def add_product_to_cart(self, user_id: str, product_id: Optional[int] = None) -> Dict[str, Any]:
        """UNIFIED: Add product to cart with consistent behavior"""
        session = self._get_or_create_session(user_id)
        
        # Determine which product to add
        product = None
        if product_id:
            product = self._find_product_by_id(product_id)
        else:
            product = self.find_last_selected_product(user_id)
        
        if not product:
            return {
                "response": "❌ No hay producto seleccionado. Por favor, elige un producto primero.",
                "buttons": [
                    {"text": "Ver productos", "callback": "btn_browse"}
                ]
            }
        
        try:
            # Add to cart
            session["cart"].append(product.copy())
            session["last_product"] = product
            
            # UNIFIED response and buttons
            return {
                "response": f"✅ {product['name']} agregado al carrito correctamente!",
                "buttons": [
                    {"text": "Ver carrito", "callback": "btn_view_cart"},
                    {"text": "Continuar comprando", "callback": "btn_browse"}
                ]
            }
        except Exception as e:
            return {
                "response": "❌ Error al agregar producto al carrito. Intenta de nuevo.",
                "buttons": [
                    {"text": "Ver productos", "callback": "btn_browse"}
                ]
            }
    
    def send_cart_confirmation_buttons(self, user_id: str) -> Dict[str, Any]:
        """UNIFIED: Send cart view with consistent formatting"""
        session = self._get_or_create_session(user_id)
        cart = session.get("cart", [])
        
        if not cart:
            return {
                "response": "🛒 Tu carrito está vacío\n¿Quieres ver nuestros productos?",
                "buttons": [
                    {"text": "Ver productos", "callback": "btn_browse"}
                ]
            }
        
        # Calculate cart summary
        total_price = sum(item["price"] for item in cart)
        item_count = len(cart)
        
        # Group items for better display
        item_counts = {}
        for item in cart:
            name = item["name"]
            if name in item_counts:
                item_counts[name]["count"] += 1
            else:
                item_counts[name] = {"item": item, "count": 1}
        
        items_text = []
        for name, data in item_counts.items():
            item = data["item"]
            count = data["count"]
            if count > 1:
                items_text.append(f"• {name} x{count} - ${item['price'] * count:.2f}")
            else:
                items_text.append(f"• {name} - ${item['price']:.2f}")
        
        response = f"🛒 Tu carrito ({item_count} items):\n" + "\n".join(items_text) + f"\n\nTotal: ${total_price:.2f}"
        
        return {
            "response": response,
            "buttons": [
                {"text": "Proceder al pago", "callback": "btn_checkout"},
                {"text": "Continuar comprando", "callback": "btn_browse"},
                {"text": "Vaciar carrito", "callback": "btn_clear_cart"}
            ]
        }
    
    def handle_product_selection(self, user_id: str, query: str) -> Dict[str, Any]:
        """UNIFIED: Handle product selection with consistent logic"""
        session = self._get_or_create_session(user_id)
        
        # Find product
        found_product = self._find_product_by_name(query)
        
        if found_product:
            # Set as last selected product
            session["last_product"] = found_product
            return {
                "response": f"📱 {found_product['name']} - ${found_product['price']:.2f}\n¿Te interesa?",
                "buttons": [
                    {"text": "Agregar al carrito", "callback": f"btn_add_{found_product['id']}"},
                    {"text": "Ver más productos", "callback": "btn_browse"}
                ]
            }
        
        return {
            "response": "❌ Producto no encontrado. ¿Quieres ver todos los productos disponibles?",
            "buttons": [
                {"text": "Ver productos", "callback": "btn_browse"}
            ]
        }
    def handle_button_press(self, user_id: str, button_data: str) -> Dict[str, Any]:
        """Handle button presses using unified functions"""
        session = self._get_or_create_session(user_id)
        
        if button_data.startswith("btn_add_"):
            # Extract product ID and use unified add function
            try:
                product_id = int(button_data.split("_")[-1])
                return self.add_product_to_cart(user_id, product_id)
            except (ValueError, IndexError):
                return {"response": "❌ Error en el botón. Intenta de nuevo."}
        
        elif button_data == "btn_view_cart":
            return self.send_cart_confirmation_buttons(user_id)
        
        elif button_data == "btn_browse":
            return self.show_products(user_id)
        
        elif button_data == "btn_clear_cart":
            return self.clear_cart(user_id)
        
        elif button_data == "btn_checkout":
            return self.process_checkout(user_id)
            
        return {"response": "❌ Botón no reconocido"}
    
    def show_products(self, user_id: str) -> Dict[str, Any]:
        """Show available products with consistent formatting"""
        buttons = []
        for product in AVAILABLE_PRODUCTS:
            buttons.append({
                "text": f"{product['name']} - ${product['price']:.2f}",
                "callback": f"btn_add_{product['id']}"
            })
        
        return {
            "response": "🏪 Productos disponibles:\nHaz clic en un producto para agregarlo al carrito:",
            "buttons": buttons
        }
    
    def clear_cart(self, user_id: str) -> Dict[str, Any]:
        """Clear the cart"""
        session = self._get_or_create_session(user_id)
        session["cart"] = []
        
        return {
            "response": "🛒 Carrito vacío correctamente.",
            "buttons": [
                {"text": "Ver productos", "callback": "btn_browse"}
            ]
        }
    
    def process_checkout(self, user_id: str) -> Dict[str, Any]:
        """Process checkout"""
        session = self._get_or_create_session(user_id)
        cart = session.get("cart", [])
        
        if not cart:
            return {
                "response": "❌ No puedes proceder al pago con un carrito vacío.",
                "buttons": [
                    {"text": "Ver productos", "callback": "btn_browse"}
                ]
            }
        
        total = sum(item["price"] for item in cart)
        
        # Clear cart after checkout
        session["cart"] = []
        session["last_product"] = None
        
        return {
            "response": f"✅ ¡Compra realizada exitosamente!\nTotal pagado: ${total:.2f}\n¡Gracias por tu compra!",
            "buttons": [
                {"text": "Comprar más", "callback": "btn_browse"}
            ]
        }
    
    def _find_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Helper: Find product by ID"""
        for product in AVAILABLE_PRODUCTS:
            if product["id"] == product_id:
                return product
        return None
    
    def _find_product_by_name(self, query: str) -> Optional[Dict[str, Any]]:
        """Helper: Find product by name in query"""
        for product in AVAILABLE_PRODUCTS:
            if product["name"].lower() in query.lower():
                return product
        return None

# Main execution with better error handling
def main():
    bot = ChatBot()
    print("🤖 Chatbot mejorado iniciado. Escribe 'quit' para salir.")
    print("Prueba comandos como: 'laptop', 'agregar al carrito', 'carrito'")
    
    user_id = "test_user"
    
    while True:
        try:
            message = input("\n> ").strip()
            if message.lower() in ['quit', 'salir', 'exit']:
                print("¡Hasta luego!")
                break
                
            if not message:
                continue
                
            response = bot.handle_message(user_id, message)
            print(f"\n🤖 Bot: {response['response']}")
            
            if "buttons" in response:
                print("\nOpciones disponibles:")
                for i, btn in enumerate(response["buttons"], 1):
                    print(f"  {i}. {btn['text']} ({btn['callback']})")
                    
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Intenta de nuevo.")

if __name__ == "__main__":
    main()