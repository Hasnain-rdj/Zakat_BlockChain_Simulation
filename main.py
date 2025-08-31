import streamlit as st
import hashlib
import json
from datetime import datetime
import time

class ZakatBlockchain:
    """
    Zakat Blockchain Simulation class that implements a blockchain system
    for tracking Zakat transactions with roll number as seed key for uniqueness.
    """
    
    def __init__(self, roll_number):
        """
        Initialize blockchain with genesis block and default balance
        
        Args:
            roll_number (str): Student's roll number used as seed key for hashing
        """
        self.roll_number = roll_number
        self.chain = []
        self.current_balance = 200  
        self.transaction_history = []
        
        # Create genesis block
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """
        Create the first block in the blockchain (genesis block)
        """
        genesis_block = {
            'index': 0,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'transactions': [{
                'type': 'Initial Balance',
                'amount': 200,
                'balance_after': 200,
                'description': 'Genesis block with initial balance'
            }],
            'previous_hash': '0',
            'roll_number_seed': self.roll_number,
            'nonce': 0
        }
        
        # Calculate hash for genesis block
        genesis_block['hash'] = self._calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        
        # Add to transaction history
        self.transaction_history.append({
            'block_index': 0,
            'transaction': genesis_block['transactions'][0]
        })
    
    def _calculate_hash(self, block):
        """
        Calculate hash for a block using roll number as seed key
        
        Args:
            block (dict): Block data to hash
            
        Returns:
            str: Calculated hash string
        """
        # Create block string excluding hash field
        block_copy = block.copy()
        if 'hash' in block_copy:
            del block_copy['hash']
        
        # Convert block to string and add roll number seed
        block_string = json.dumps(block_copy, sort_keys=True) + str(self.roll_number)
        
        # Calculate SHA-256 hash
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def calculate_zakat(self, balance):
        """
        Calculate 2.5% Zakat from given balance
        
        Args:
            balance (float): Current balance
            
        Returns:
            float: Zakat amount (2.5% of balance)
        """
        return round(balance * 0.025, 2)
    
    def deduct_zakat(self, description="Zakat Deduction"):
        """
        Deduct Zakat from current balance and create a new block
        
        Args:
            description (str): Description for the transaction
            
        Returns:
            dict: Result of the transaction
        """
        if self.current_balance <= 0:
            return {
                'success': False,
                'message': 'Insufficient balance for Zakat deduction'
            }
        
        # Calculate Zakat amount
        zakat_amount = self.calculate_zakat(self.current_balance)
        
        # Update balance
        previous_balance = self.current_balance
        self.current_balance = round(self.current_balance - zakat_amount, 2)
        
        # Create transaction
        transaction = {
            'type': 'Zakat Deduction',
            'amount': -zakat_amount,
            'balance_before': previous_balance,
            'balance_after': self.current_balance,
            'zakat_percentage': 2.5,
            'description': description,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create new block
        new_block = {
            'index': len(self.chain),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'transactions': [transaction],
            'previous_hash': self.chain[-1]['hash'] if self.chain else '0',
            'roll_number_seed': self.roll_number,
            'nonce': 0
        }
        
        # Calculate hash for new block
        new_block['hash'] = self._calculate_hash(new_block)
        
        # Add block to chain
        self.chain.append(new_block)
        
        # Add to transaction history
        self.transaction_history.append({
            'block_index': new_block['index'],
            'transaction': transaction
        })
        
        return {
            'success': True,
            'message': f'Zakat of {zakat_amount} coins deducted successfully',
            'zakat_amount': zakat_amount,
            'remaining_balance': self.current_balance,
            'block_hash': new_block['hash']
        }
    
    def add_custom_transaction(self, amount, transaction_type, description="Custom Transaction"):
        """
        Add a custom transaction (for simulation purposes)
        
        Args:
            amount (float): Transaction amount (positive for credit, negative for debit)
            transaction_type (str): Type of transaction
            description (str): Description for the transaction
            
        Returns:
            dict: Result of the transaction
        """
        if self.current_balance + amount < 0:
            return {
                'success': False,
                'message': 'Transaction would result in negative balance'
            }
        
        # Update balance
        previous_balance = self.current_balance
        self.current_balance = round(self.current_balance + amount, 2)
        
        # Create transaction
        transaction = {
            'type': transaction_type,
            'amount': amount,
            'balance_before': previous_balance,
            'balance_after': self.current_balance,
            'description': description,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create new block
        new_block = {
            'index': len(self.chain),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'transactions': [transaction],
            'previous_hash': self.chain[-1]['hash'] if self.chain else '0',
            'roll_number_seed': self.roll_number,
            'nonce': 0
        }
        
        # Calculate hash for new block
        new_block['hash'] = self._calculate_hash(new_block)
        
        # Add block to chain
        self.chain.append(new_block)
        
        # Add to transaction history
        self.transaction_history.append({
            'block_index': new_block['index'],
            'transaction': transaction
        })
        
        return {
            'success': True,
            'message': f'Transaction of {amount} coins processed successfully',
            'remaining_balance': self.current_balance,
            'block_hash': new_block['hash']
        }
    
    def validate_blockchain(self):
        """
        Validate the entire blockchain for integrity and immutability
        
        Returns:
            dict: Validation result with details
        """
        validation_errors = []
        
        for i in range(len(self.chain)):
            current_block = self.chain[i]
            
            # Check if hash is correct
            calculated_hash = self._calculate_hash(current_block)
            if current_block['hash'] != calculated_hash:
                validation_errors.append(f"Block {i}: Hash mismatch")
            
            # Check if previous hash is correct (except for genesis block)
            if i > 0:
                previous_block = self.chain[i-1]
                if current_block['previous_hash'] != previous_block['hash']:
                    validation_errors.append(f"Block {i}: Previous hash mismatch")
            
            # Check if roll number seed is consistent
            if current_block['roll_number_seed'] != self.roll_number:
                validation_errors.append(f"Block {i}: Roll number seed mismatch")
        
        return {
            'is_valid': len(validation_errors) == 0,
            'errors': validation_errors,
            'total_blocks': len(self.chain)
        }
    
    def get_blockchain_info(self):
        """
        Get comprehensive information about the blockchain
        
        Returns:
            dict: Blockchain information
        """
        return {
            'total_blocks': len(self.chain),
            'current_balance': self.current_balance,
            'roll_number': self.roll_number,
            'total_transactions': len(self.transaction_history),
            'last_block_hash': self.chain[-1]['hash'] if self.chain else None,
            'blockchain_valid': self.validate_blockchain()['is_valid']
        }


def main():
    """
    Main Streamlit application for Zakat Blockchain Simulation
    """
    st.set_page_config(
        page_title="Zakat Blockchain Simulation",
        page_icon="🔗",
        layout="wide"
    )
    
    st.title("🔗 Zakat Blockchain Simulation")
    st.markdown("---")
    
    # Initialize session state
    if 'blockchain' not in st.session_state:
        st.session_state.blockchain = None
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Roll number input
    roll_number = st.sidebar.text_input(
        "Enter Your Roll Number",
        value="",
        help="This will be used as a seed key for hashing"
    )
    
    # Initialize blockchain button
    if st.sidebar.button("Initialize Blockchain", type="primary"):
        if roll_number:
            st.session_state.blockchain = ZakatBlockchain(roll_number)
            st.sidebar.success(f"Blockchain initialized for Roll Number: {roll_number}")
        else:
            st.sidebar.error("Please enter a roll number")
    
    # Main content
    if st.session_state.blockchain is None:
        st.info("👈 Please enter your roll number and initialize the blockchain to get started")
        
        # Display requirements and information
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Project Requirements")
            st.markdown("""
            - **Starting Balance**: 200 coins per node
            - **Zakat Rate**: 2.5% deduction
            - **Hashing**: SHA-256 with roll number seed
            - **Immutability**: Hash-based block validation
            - **Transaction History**: Complete ledger maintenance
            """)
        
        with col2:
            st.subheader("🔧 Technical Specifications")
            st.markdown("""
            - **Implementation**: Pure Python (no external blockchain libraries)
            - **Data Structures**: Lists and Dictionaries only
            - **Security**: Roll number ensures hash uniqueness
            - **Validation**: Complete blockchain integrity checks
            - **Transparency**: Full transaction traceability
            """)
    
    else:
        blockchain = st.session_state.blockchain
        
        # Display current status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Balance", f"{blockchain.current_balance} coins")
        
        with col2:
            st.metric("Total Blocks", len(blockchain.chain))
        
        with col3:
            st.metric("Total Transactions", len(blockchain.transaction_history))
        
        with col4:
            validation = blockchain.validate_blockchain()
            st.metric("Blockchain Status", "✅ Valid" if validation['is_valid'] else "❌ Invalid")
        
        st.markdown("---")
        
        # Main operations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💰 Zakat Operations", 
            "💳 Custom Transactions", 
            "🔗 Blockchain View", 
            "📊 Transaction History", 
            "🔍 Validation"
        ])
        
        with tab1:
            st.subheader("Zakat Deduction (2.5%)")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if blockchain.current_balance > 0:
                    zakat_amount = blockchain.calculate_zakat(blockchain.current_balance)
                    st.info(f"Current Zakat amount: {zakat_amount} coins (2.5% of {blockchain.current_balance})")
                    
                    description = st.text_input("Transaction Description", value="Zakat Deduction")
                    
                    if st.button("Deduct Zakat", type="primary"):
                        result = blockchain.deduct_zakat(description)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                else:
                    st.warning("Insufficient balance for Zakat deduction")
            
            with col2:
                st.markdown("**Zakat Calculation**")
                st.code(f"""
Balance: {blockchain.current_balance}
Rate: 2.5%
Zakat: {blockchain.calculate_zakat(blockchain.current_balance)}
                """)
        
        with tab2:
            st.subheader("Custom Transactions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.selectbox(
                    "Transaction Type",
                    ["Income", "Expense", "Transfer", "Other"]
                )
                
                amount = st.number_input(
                    "Amount (positive for credit, negative for debit)",
                    value=0.0,
                    step=0.01
                )
                
                description = st.text_input("Description", value="Custom Transaction")
                
                if st.button("Add Transaction"):
                    result = blockchain.add_custom_transaction(amount, transaction_type, description)
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
            
            with col2:
                st.markdown("**Transaction Preview**")
                if amount != 0:
                    new_balance = blockchain.current_balance + amount
                    st.code(f"""
Current Balance: {blockchain.current_balance}
Transaction: {amount:+}
New Balance: {new_balance}
                    """)
        
        with tab3:
            st.subheader("Blockchain Structure")
            
            for i, block in enumerate(blockchain.chain):
                with st.expander(f"Block {i} - {block['timestamp']}", expanded=(i == len(blockchain.chain) - 1)):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Block Information**")
                        st.json({
                            'Index': block['index'],
                            'Timestamp': block['timestamp'],
                            'Previous Hash': block['previous_hash'][:16] + "...",
                            'Current Hash': block['hash'][:16] + "...",
                            'Roll Number Seed': block['roll_number_seed']
                        })
                    
                    with col2:
                        st.markdown("**Transactions**")
                        for transaction in block['transactions']:
                            st.json(transaction)
        
        with tab4:
            st.subheader("Complete Transaction History")
            
            if blockchain.transaction_history:
                for i, record in enumerate(reversed(blockchain.transaction_history)):
                    transaction = record['transaction']
                    block_index = record['block_index']
                    
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
                        
                        with col1:
                            st.write(f"**Block {block_index}**")
                        
                        with col2:
                            st.write(f"**{transaction['type']}**")
                        
                        with col3:
                            amount = transaction['amount']
                            color = "green" if amount > 0 else "red"
                            st.markdown(f"<span style='color: {color}'>{amount:+} coins</span>", unsafe_allow_html=True)
                        
                        with col4:
                            if 'balance_after' in transaction:
                                st.write(f"Balance: {transaction['balance_after']}")
                        
                        st.caption(transaction.get('description', 'No description'))
                        if i < len(blockchain.transaction_history) - 1:
                            st.divider()
            else:
                st.info("No transactions yet")
        
        with tab5:
            st.subheader("Blockchain Validation")
            
            validation = blockchain.validate_blockchain()
            
            if validation['is_valid']:
                st.success("✅ Blockchain is valid and secure!")
            else:
                st.error("❌ Blockchain validation failed!")
                for error in validation['errors']:
                    st.error(f"• {error}")
            
            # Detailed validation info
            st.markdown("**Validation Details**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Blocks Checked", validation['total_blocks'])
                st.metric("Validation Errors", len(validation['errors']))
            
            with col2:
                info = blockchain.get_blockchain_info()
                st.json({
                    'Roll Number': info['roll_number'],
                    'Current Balance': info['current_balance'],
                    'Last Block Hash': info['last_block_hash'][:16] + "..." if info['last_block_hash'] else "None",
                    'Blockchain Valid': info['blockchain_valid']
                })
            
            # Manual validation button
            if st.button("Re-validate Blockchain"):
                st.rerun()


if __name__ == "__main__":
    main()