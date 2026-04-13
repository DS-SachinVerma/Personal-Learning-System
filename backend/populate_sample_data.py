#!/usr/bin/env python3
"""
Sample data insertion script for the Learning Management System.
This script populates the database with example resources, notes, and tasks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Resource, Note, Task
from sqlalchemy.orm import sessionmaker

def create_sample_data():
    """Create sample data for demonstration purposes."""

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Sample Resources
        resources = [
            Resource(
                title="Deep Learning Specialization",
                link="https://www.coursera.org/specializations/deep-learning",
                type="course",
                status="to_learn",
                tags="deep-learning,machine-learning,neural-networks,andrew-ng",
                notes="Andrew Ng's comprehensive deep learning course covering neural networks, CNNs, RNNs, and more."
            ),
            Resource(
                title="Attention Is All You Need",
                link="https://arxiv.org/abs/1706.03762",
                type="paper",
                status="learning",
                tags="transformers,attention,nlp,paper",
                notes="The seminal paper introducing the Transformer architecture that revolutionized NLP."
            ),
            Resource(
                title="Fast.ai Practical Deep Learning",
                link="https://course.fast.ai/",
                type="course",
                status="to_learn",
                tags="deep-learning,fastai,jeremy-howard,practical",
                notes="Jeremy Howard's practical deep learning course with cutting-edge techniques."
            ),
            Resource(
                title="Reinforcement Learning: An Introduction",
                link="http://incompleteideas.net/book/the-book-2nd.html",
                type="book",
                status="learning",
                tags="reinforcement-learning,rl,textbook,sutton-barto",
                notes="The definitive textbook on reinforcement learning by Sutton and Barto."
            ),
            Resource(
                title="Hugging Face Transformers",
                link="https://huggingface.co/docs/transformers/index",
                type="documentation",
                status="to_learn",
                tags="transformers,huggingface,nlp,library",
                notes="Comprehensive documentation for the Hugging Face Transformers library."
            ),
            Resource(
                title="Stanford CS231n: Convolutional Neural Networks",
                link="https://cs231n.github.io/",
                type="course",
                status="to_learn",
                tags="computer-vision,cnn,stanford,deep-learning",
                notes="Stanford's computer vision course covering CNNs and modern deep learning techniques."
            ),
            Resource(
                title="The Illustrated Transformer",
                link="http://jalammar.github.io/illustrated-transformer/",
                type="blog",
                status="completed",
                tags="transformers,visualization,jay-alammar,explanation",
                notes="Jay Alammar's visual guide to understanding Transformer architecture."
            ),
            Resource(
                title="PyTorch Official Tutorials",
                link="https://pytorch.org/tutorials/",
                type="documentation",
                status="to_learn",
                tags="pytorch,tutorials,deep-learning,official",
                notes="Official PyTorch tutorials covering everything from basics to advanced topics."
            )
        ]

        # Add resources to session
        for resource in resources:
            session.add(resource)

        # Commit resources to get IDs
        session.commit()

        # Sample Notes
        notes = [
            Note(
                title="Neural Network Fundamentals",
                content="""# Neural Network Basics

## Key Concepts
- **Neurons**: Basic computational units that receive inputs, apply weights, and produce outputs through activation functions
- **Layers**: Input layer, hidden layers, output layer
- **Weights & Biases**: Parameters that the network learns during training
- **Activation Functions**: Non-linear functions like ReLU, sigmoid, tanh

## Forward Propagation
The process of passing input data through the network:
1. Input → Weighted sum → Activation function → Output
2. Repeat for each layer until final output

## Backpropagation
How neural networks learn:
1. Calculate loss (error) between prediction and actual
2. Compute gradients using chain rule
3. Update weights using gradient descent

## Common Architectures
- **Feedforward NN**: Basic architecture, no cycles
- **CNN**: Convolutional Neural Networks for image data
- **RNN**: Recurrent Neural Networks for sequential data
- **Transformer**: Attention-based architecture for sequences

## Training Tips
- Normalize input data
- Use appropriate learning rates
- Regularization techniques (dropout, L2)
- Monitor for overfitting""",
                tags="neural-networks,fundamentals,deep-learning",
                linked_resource_id=1
            ),
            Note(
                title="Transformer Architecture Deep Dive",
                content="""# Understanding Transformers

## Core Components

### Self-Attention Mechanism
- **Query, Key, Value**: Three learned projections of input embeddings
- **Attention Scores**: Computed as Q·K^T / √d_k
- **Weighted Sum**: Values weighted by attention scores

### Multi-Head Attention
- Multiple attention heads run in parallel
- Each head learns different attention patterns
- Concatenated outputs passed through linear layer

### Positional Encoding
- Since transformers have no recurrence, need to inject position information
- Uses sinusoidal functions: PE(pos,2i) = sin(pos/10000^(2i/d))
- Allows model to understand sequence order

### Feed-Forward Networks
- Position-wise fully connected networks
- Applied to each position independently
- Consists of two linear transformations with ReLU

## Encoder-Decoder Structure
- **Encoder**: Processes input sequence → context representations
- **Decoder**: Generates output sequence using encoder context
- **Cross-Attention**: Decoder attends to encoder outputs

## Key Advantages
- Parallelizable (unlike RNNs)
- Long-range dependencies captured effectively
- No vanishing gradient problem
- Scalable to very long sequences

## Applications
- Machine Translation
- Text Summarization
- Question Answering
- Code Generation
- Image Captioning""",
                tags="transformers,attention,nlp,architecture",
                linked_resource_id=2
            ),
            Note(
                title="Reinforcement Learning Fundamentals",
                content="""# Reinforcement Learning Basics

## Core Concepts

### Agent-Environment Interaction
- **Agent**: Learns to make decisions
- **Environment**: Provides feedback to agent
- **State**: Current situation of the environment
- **Action**: What the agent can do
- **Reward**: Feedback signal from environment

### Markov Decision Processes (MDPs)
- **States**: Set of all possible situations
- **Actions**: Available actions in each state
- **Transition Probabilities**: P(s'|s,a)
- **Rewards**: R(s,a,s') or R(s,a)
- **Discount Factor**: γ ∈ [0,1]

### Value Functions
- **State Value V(s)**: Expected return from state s
- **Action Value Q(s,a)**: Expected return from state s taking action a
- **Bellman Equations**: Recursive relationships for value functions

## Learning Algorithms

### Q-Learning
- Model-free algorithm
- Learns Q-values directly
- Uses temporal difference learning
- Off-policy: learns from any policy

### SARSA
- On-policy version of Q-learning
- Learns from actions actually taken
- More conservative than Q-learning

### Policy Gradient Methods
- Learn policy directly (not value function)
- Use gradient ascent on expected return
- Can handle continuous action spaces

## Exploration vs Exploitation
- **ε-greedy**: Random action with probability ε
- **Softmax**: Probabilistic action selection
- **Upper Confidence Bound (UCB)**: Balances exploration/exploitation

## Applications
- Game playing (AlphaGo, Dota 2)
- Robotics
- Recommendation systems
- Autonomous vehicles
- Resource management""",
                tags="reinforcement-learning,rl,mdp,value-functions",
                linked_resource_id=4
            ),
            Note(
                title="CNN Architecture Patterns",
                content="""# Convolutional Neural Networks

## Basic Building Blocks

### Convolutional Layers
- **Filters/Kernels**: Learnable feature detectors
- **Stride**: Step size for sliding window
- **Padding**: Maintain spatial dimensions
- **Feature Maps**: Output of convolution operations

### Pooling Layers
- **Max Pooling**: Take maximum value in window
- **Average Pooling**: Take average value in window
- **Global Average Pooling**: Pool entire feature map

### Activation Functions
- **ReLU**: max(0,x) - most common
- **Leaky ReLU**: max(αx,x) - avoids dead neurons
- **ELU**: Exponential Linear Unit
- **Swish**: x * sigmoid(x)

## Modern Architectures

### ResNet (Residual Networks)
- **Residual Connections**: Skip connections that add input to output
- **Identity Mapping**: F(x) + x
- **Deep Networks**: Enables training of very deep networks (1000+ layers)

### DenseNet
- **Dense Connections**: Each layer connected to all subsequent layers
- **Feature Reuse**: Concatenation instead of addition
- **Parameter Efficiency**: Fewer parameters than ResNet

### EfficientNet
- **Compound Scaling**: Scale depth, width, resolution together
- **Mobile-Friendly**: Efficient for mobile deployment
- **NAS**: Neural Architecture Search derived

## Design Patterns
- **Stem**: Initial convolution + pooling
- **Body**: Repeated blocks with increasing channels
- **Head**: Global pooling + classification layers

## Training Considerations
- **Data Augmentation**: Random crops, flips, color jittering
- **Regularization**: Dropout, batch normalization
- **Learning Rate Scheduling**: Cosine annealing, step decay
- **Transfer Learning**: Fine-tune pretrained models""",
                tags="cnn,computer-vision,architectures,resnet",
                linked_resource_id=6
            ),
            Note(
                title="PyTorch Best Practices",
                content="""# PyTorch Development Tips

## Data Loading & Processing
```python
# Use DataLoader for efficient batching
from torch.utils.data import DataLoader, Dataset

class CustomDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# Pin memory for faster GPU transfer
dataloader = DataLoader(dataset, batch_size=32, pin_memory=True, num_workers=4)
```

## Model Definition
```python
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )

    def forward(self, x):
        return self.layers(x)
```

## Training Loop
```python
def train_epoch(model, dataloader, optimizer, criterion, device):
    model.train()
    total_loss = 0

    for batch in dataloader:
        inputs, targets = batch
        inputs, targets = inputs.to(device), targets.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)
```

## GPU Utilization
- Use `.to(device)` for tensor/device placement
- Enable cuDNN benchmark mode: `torch.backends.cudnn.benchmark = True`
- Use mixed precision training with `torch.cuda.amp`

## Debugging
- `torchsummary` for model architecture visualization
- `torchviz` for computational graph visualization
- Gradient checking with `torch.autograd.gradcheck`
- Memory profiling with `torch.cuda.memory_summary()`

## Performance Optimization
- Use `torch.compile()` (PyTorch 2.0+)
- Profile with `torch.profiler`
- Use `torch.jit.trace` or `torch.jit.script` for inference
- Quantization for deployment""",
                tags="pytorch,best-practices,training,gpu",
                linked_resource_id=8
            )
        ]

        # Add notes to session
        for note in notes:
            session.add(note)

        # Sample Tasks
        tasks = [
            Task(
                task="Complete Neural Networks Coursera Course",
                status="in_progress",
                priority="high"
            ),
            Task(
                task="Implement Transformer from Scratch",
                status="pending",
                priority="high"
            ),
            Task(
                task="Read Reinforcement Learning Textbook",
                status="in_progress",
                priority="high"
            ),
            Task(
                task="Build CNN Image Classifier",
                status="completed",
                priority="medium"
            ),
            Task(
                task="Experiment with Attention Mechanisms",
                status="pending",
                priority="high"
            ),
            Task(
                task="Set up ML Experiment Tracking",
                status="pending",
                priority="low"
            ),
            Task(
                task="Learn Fast.ai Library",
                status="pending",
                priority="medium"
            ),
            Task(
                task="Contribute to Open Source ML Project",
                status="pending",
                priority="medium"
            )
        ]

        # Add tasks to session
        for task in tasks:
            session.add(task)

        # Commit all changes
        session.commit()

        print("✅ Sample data inserted successfully!")
        print(f"📚 Added {len(resources)} resources")
        print(f"📝 Added {len(notes)} notes")
        print(f"✅ Added {len(tasks)} tasks")

    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting sample data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("🌱 Inserting sample data into learning management system...")
    create_sample_data()
    print("🎉 Database populated with sample data!")