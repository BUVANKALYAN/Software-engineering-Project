let currentStep = 0;
let selectedEvent = null;
const availableEvents = [
    { name: "Tech Conference 2024", location: "New York", date: "2024-05-12", occupancy: 500 },
    { name: "Music Festival", location: "Los Angeles", date: "2024-06-20", occupancy: 3000 },
    { name: "Art Expo", location: "Chicago", date: "2024-07-15", occupancy: 200 }
];

// Initialize the chat interface
document.addEventListener("DOMContentLoaded", function() {
    const sendButton = document.querySelector(".send-button");
    const userInput = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");

    // Initial bot message
    setTimeout(() => {
        displayMessage('bot', "Hello! Are you here to participate in an event or arrange one?");
        createButtons(['Participate', 'Arrange']);
    }, 500);

    // Handle send button click
    sendButton.addEventListener("click", () => sendMessage());

    // Handle enter key press
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    // Ensure chat box is always scrolled to bottom when new content is added
    const observer = new MutationObserver(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    observer.observe(chatBox, { childList: true });
});

function sendMessage() {
    const userInput = document.getElementById("userInput");
    const message = userInput.value.trim();
    
    if (message === "") return;

    // Display user message
    displayMessage('user', message);
    
    // Clear input field
    userInput.value = "";
    
    // Process the message
    processUserInput(message);
}

function displayMessage(sender, message) {
    const chatBox = document.getElementById("chatBox");
    const messageDiv = document.createElement("div");
    messageDiv.className = sender === 'user' ? "user-message" : "bot-message";
    
    // Handle multiline messages
    const formattedMessage = message.split('\n').map(line => {
        return line.trim();
    }).join('<br>');
    
    messageDiv.innerHTML = formattedMessage;
    chatBox.appendChild(messageDiv);
}

function createButtons(options) {
    const chatButtons = document.getElementById("chatButtons");
    const userInput = document.getElementById("userInput");
    const inputArea = document.querySelector(".chat-input");
    
    // Clear existing buttons
    chatButtons.innerHTML = '';
    
    if (options.length === 0) {
        // Show input area when no buttons
        inputArea.style.display = 'flex';
        chatButtons.style.display = 'none';
        return;
    }

    // Create new buttons
    options.forEach(option => {
        const button = document.createElement("button");
        button.textContent = option;
        button.onclick = () => {
            displayMessage('user', option);
            processUserInput(option);
        };
        chatButtons.appendChild(button);
    });

    // Show buttons, hide input area
    chatButtons.style.display = 'flex';
    inputArea.style.display = 'none';
}

const eventTypes = {
    "conference": {
        basePrice: 1000,
        amenities: ["Stage setup", "Audio system", "Projector", "Chairs", "Registration desk", "Air conditioning", "Wifi"],
        locations: {
            "Chennai Trade Centre, Nandambakkam": { capacity: 2000, cost: 100000 },
            "ITC Grand Chola, Guindy": { capacity: 1000, cost: 150000 },
            "Chennai Convention Centre, Nandanam": { capacity: 1500, cost: 120000 }
        }
    },
    "cultural": {
        basePrice: 800,
        amenities: ["Stage setup", "Dance floor", "Audio system", "Lighting", "Chairs", "Food court", "Green room"],
        locations: {
            "VGP Golden Beach Resort": { capacity: 3000, cost: 200000 },
            "Mayor Ramanathan Centre": { capacity: 1000, cost: 80000 },
            "Kamarajar Arangam": { capacity: 2500, cost: 150000 }
        }
    },
    "exhibition": {
        basePrice: 500,
        amenities: ["Stalls", "Audio system", "Lighting", "Security", "Parking", "Food court"],
        locations: {
            "Chennai Trade Centre": { capacity: 5000, cost: 250000 },
            "Chennai Convention Centre": { capacity: 2000, cost: 120000 },
            "Express Avenue Convention Hall": { capacity: 1000, cost: 100000 }
        }
    }
};

function processUserInput(input) {
    switch (currentStep) {
        case 0:
            if (input.toLowerCase() === 'participate') {
                displayMessage('bot', "Here are the available events. Click on an event to view its details.");
                displayEventsAsButtons();
                currentStep = 1;
            } else if (input.toLowerCase() === 'arrange') {
                displayMessage('bot', "What is the name of the event you want to arrange?");
                createButtons([]); // Show text input
                currentStep = 10;
            } else {
                displayMessage('bot', "Please select 'Participate' or 'Arrange'.");
                createButtons(['Participate', 'Arrange']);
            }
            break;

        case 1:
            const selectedEvent = availableEvents.find(e => e.name === input);
            if (selectedEvent) {
                displayEventDetails(selectedEvent);
                createButtons(['Yes, Participate', 'No, Not Interested']);
                currentStep = 2;
            } else {
                displayMessage('bot', "Please select a valid event.");
                displayEventsAsButtons();
            }
            break;

        case 2:
            if (input === 'Yes, Participate') {
                displayMessage('bot', "Redirecting to payment page... 💳");
                handlePayment();
                currentStep = 3;
            } else if (input === 'No, Not Interested') {
                displayMessage('bot', "No problem! Here are other events you might be interested in:");
                displayEventsAsButtons();
                currentStep = 1;
            }
            break;

        case 3:
            displayMessage('bot', "Please enter your email to receive the event details. ✉️");
            createButtons([]); // Show text input
            currentStep = 4;
            break;

        case 4:
            if (validateEmail(input)) {
                // Send registration request to server
                fetch('/process_event_registration', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: input,
                        event_name: selectedEvent.name
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayMessage('bot', `✨ Registration successful! Your ticket has been sent to ${input}`);
                        displayMessage('bot', `🎫 Your ticket number: ${data.ticket_number}`);
                        displayMessage('bot', "Would you like to view more events?");
                        createButtons(['Yes', 'No']);
                        currentStep = 5;
                    } else {
                        displayMessage('bot', "❌ There was an error processing your registration. Please try again.");
                        createButtons([]); // Keep text input visible
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    displayMessage('bot', "❌ There was an error processing your registration. Please try again.");
                    createButtons([]); // Keep text input visible
                });
            } else {
                displayMessage('bot', "Please enter a valid email address.");
                createButtons([]); // Keep text input visible
            }
            break;

        case 10:
            // Handle event arrangement flow
            displayMessage('bot', `Great! You want to arrange an event called "${input}". Please provide the event date:`);
            createButtons([]); // Keep text input for date
            currentStep = 11;
            break;

            case 10:
                eventDetails = { name: input };
                displayMessage('bot', `Great! You want to arrange "${input}". What type of event is this?`);
                createButtons(Object.keys(eventTypes));
                currentStep = 11;
                break;
    
            case 11:
                if (eventTypes[input.toLowerCase()]) {
                    eventDetails.type = input.toLowerCase();
                    displayMessage('bot', "Please enter the expected number of attendees:");
                    createButtons([]);
                    currentStep = 12;
                } else {
                    displayMessage('bot', "Please select a valid event type:");
                    createButtons(Object.keys(eventTypes));
                }
                break;
    
            case 12:
                const attendees = parseInt(input);
                if (!isNaN(attendees) && attendees > 0) {
                    eventDetails.attendees = attendees;
                    displayMessage('bot', "Please enter the ticket price per person (in ₹):");
                    createButtons([]);
                    currentStep = 13;
                } else {
                    displayMessage('bot', "Please enter a valid number of attendees:");
                    createButtons([]);
                }
                break;
    
            case 13:
                const ticketPrice = parseInt(input);
                if (!isNaN(ticketPrice) && ticketPrice > 0) {
                    eventDetails.ticketPrice = ticketPrice;
                    displayMessage('bot', "Please enter the preferred date (YYYY-MM-DD):");
                    createButtons([]);
                    currentStep = 14;
                } else {
                    displayMessage('bot', "Please enter a valid ticket price:");
                    createButtons([]);
                }
                break;
    
            case 14:
                if (validateDate(input)) {
                    eventDetails.date = input;
                    const suggestion = generateEventSuggestion(eventDetails);
                    displayEventSuggestion(suggestion);
                    createButtons(['Accept Budget', 'Reduce Budget']);
                    currentStep = 15;
                } else {
                    displayMessage('bot', "Please enter a valid date (YYYY-MM-DD):");
                    createButtons([]);
                }
                break;
    
            case 15:
                if (input === 'Accept Budget') {
                    displayMessage('bot', "Great! Let's proceed with the payment. Please enter your email address:");
                    createButtons([]);
                    currentStep = 16;
                } else if (input === 'Reduce Budget') {
                    const reducedSuggestion = reduceEventBudget(eventDetails.currentSuggestion);
                    if (reducedSuggestion) {
                        eventDetails.currentSuggestion = reducedSuggestion;
                        displayEventSuggestion(reducedSuggestion);
                        createButtons(['Accept Budget', 'Reduce Budget']);
                    } else {
                        displayMessage('bot', "Sorry, we cannot reduce the budget further while maintaining event quality.");
                        createButtons(['Accept Original Budget', 'Cancel']);
                    }
                }
                break;
    
            case 16:
                if (validateEmail(input)) {
                    eventDetails.email = input;
                    processEventPayment(eventDetails);
                } else {
                    displayMessage('bot', "Please enter a valid email address:");
                    createButtons([]);
                }
                break;
        }
    }

function displayEventsAsButtons() {
    createButtons(availableEvents.map(event => event.name));
}

function displayEventDetails(event) {
    const details = `
📅 Event: ${event.name}
📍 Location: ${event.location}
🗓️ Date: ${event.date}
👥 Occupancy: ${event.occupancy}`;
    displayMessage('bot', details);
}

function handlePayment() {
    // Simulate payment process
    setTimeout(() => {
        displayMessage('bot', "Payment successful! 🎉");
        processUserInput("PAYMENT_COMPLETE");
    }, 2000);
}

function validateEmail(email) {
    return email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
}

function validateDate(date) {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(date)) return false;
    
    const d = new Date(date);
    const today = new Date();
    return d instanceof Date && !isNaN(d) && d > today;
}

function generateEventSuggestion(details) {
    const eventType = eventTypes[details.type];
    const validLocations = Object.entries(eventType.locations)
        .filter(([_, loc]) => loc.capacity >= details.attendees)
        .sort((a, b) => a[1].cost - b[1].cost);

    if (validLocations.length === 0) {
        return null;
    }

    const location = validLocations[0];
    const baseAmenities = [...eventType.amenities];
    
    // Calculate costs
    const venueCost = location[1].cost;
    const expectedRevenue = details.attendees * details.ticketPrice;
    const amenitiesCost = baseAmenities.length * 10000; // ₹10,000 per amenity
    const staffCost = Math.ceil(details.attendees / 50) * 2000; // One staff per 50 attendees
    const marketingCost = Math.min(expectedRevenue * 0.1, 50000); // 10% of revenue or max ₹50,000
    
    const totalCost = venueCost + amenitiesCost + staffCost + marketingCost;
    
    return {
        location: location[0],
        amenities: baseAmenities,
        costs: {
            venue: venueCost,
            amenities: amenitiesCost,
            staff: staffCost,
            marketing: marketingCost,
            total: totalCost
        },
        expectedRevenue: expectedRevenue,
        profit: expectedRevenue - totalCost
    };
}

function displayEventSuggestion(suggestion) {
    if (!suggestion) {
        displayMessage('bot', "Sorry, we couldn't find a suitable venue for your event size.");
        return;
    }

    const message = `
📋 Event Suggestion Summary:
📍 Recommended Venue: ${suggestion.location}

💰 Cost Breakdown:
   • Venue: ₹${suggestion.costs.venue.toLocaleString()}
   • Amenities: ₹${suggestion.costs.amenities.toLocaleString()}
   • Staff: ₹${suggestion.costs.staff.toLocaleString()}
   • Marketing: ₹${suggestion.costs.marketing.toLocaleString()}
   
📊 Financial Summary:
   • Total Cost: ₹${suggestion.costs.total.toLocaleString()}
   • Expected Revenue: ₹${suggestion.expectedRevenue.toLocaleString()}
   • Estimated Profit: ₹${suggestion.profit.toLocaleString()}

✨ Included Amenities:
${suggestion.amenities.map(a => `   • ${a}`).join('\n')}

Would you like to proceed with this budget?`;

    displayMessage('bot', message);
}

function reduceEventBudget(suggestion) {
    if (!suggestion || suggestion.amenities.length <= 3) {
        return null;
    }

    // Remove one amenity
    const reducedAmenities = [...suggestion.amenities];
    reducedAmenities.pop();

    // Reduce costs
    const reducedCosts = {
        ...suggestion.costs,
        amenities: reducedAmenities.length * 10000,
    };
    reducedCosts.total = reducedCosts.venue + reducedCosts.amenities + 
                        reducedCosts.staff + reducedCosts.marketing;

    return {
        ...suggestion,
        amenities: reducedAmenities,
        costs: reducedCosts,
        profit: suggestion.expectedRevenue - reducedCosts.total
    };
}

function processEventPayment(eventDetails) {
    // Simulate payment processing
    displayMessage('bot', "Processing payment...");
    setTimeout(() => {
        displayMessage('bot', `✅ Payment successful! Event "${eventDetails.name}" has been scheduled.`);
        displayMessage('bot', `📧 Confirmation email sent to ${eventDetails.email}`);
        displayMessage('bot', "Would you like to arrange another event?");
        createButtons(['Yes', 'No']);
        currentStep = 0;
    }, 2000);
}