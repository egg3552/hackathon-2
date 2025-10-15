/**
 * Main JavaScript file for Meeting Notes App
 * Contains helper functions and shared functionality
 */

// Display flash message
function showFlashMessage(message, category = 'info') {
    const flashContainer = document.getElementById('flashMessages');
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    flashContainer.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Logout functionality
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/auth/api/logout', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    showFlashMessage('Logged out successfully!', 'success');
                    setTimeout(() => {
                        window.location.href = '/auth/login';
                    }, 1000);
                } else {
                    showFlashMessage('Logout failed', 'danger');
                }
            } catch (error) {
                showFlashMessage('An error occurred during logout', 'danger');
            }
        });
    }
});

/**
 * Example Fetch API calls for CRUD operations
 */

// GET request example
async function fetchMeetings(searchQuery = '', dateFilter = '') {
    try {
        let url = '/api/meetings?';
        if (searchQuery) {
            url += `search=${encodeURIComponent(searchQuery)}&`;
        }
        if (dateFilter) {
            url += `date=${dateFilter}&`;
        }
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching meetings:', error);
        showFlashMessage('Failed to load meetings', 'danger');
        return null;
    }
}

// POST request example
async function createMeeting(meetingData) {
    try {
        const response = await fetch('/api/meetings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(meetingData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to create meeting');
        }
        
        showFlashMessage('Meeting created successfully!', 'success');
        return data;
    } catch (error) {
        console.error('Error creating meeting:', error);
        showFlashMessage(error.message, 'danger');
        return null;
    }
}

// PUT request example
async function updateMeeting(meetingId, meetingData) {
    try {
        const response = await fetch(`/api/meetings/${meetingId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(meetingData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to update meeting');
        }
        
        showFlashMessage('Meeting updated successfully!', 'success');
        return data;
    } catch (error) {
        console.error('Error updating meeting:', error);
        showFlashMessage(error.message, 'danger');
        return null;
    }
}

// DELETE request example
async function deleteMeetingAPI(meetingId) {
    try {
        const response = await fetch(`/api/meetings/${meetingId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to delete meeting');
        }
        
        showFlashMessage('Meeting deleted successfully!', 'success');
        return data;
    } catch (error) {
        console.error('Error deleting meeting:', error);
        showFlashMessage(error.message, 'danger');
        return null;
    }
}

// Note CRUD examples
async function createNote(meetingId, content) {
    try {
        const response = await fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                meeting_id: meetingId,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to create note');
        }
        
        showFlashMessage('Note added successfully!', 'success');
        return data;
    } catch (error) {
        console.error('Error creating note:', error);
        showFlashMessage(error.message, 'danger');
        return null;
    }
}

async function updateNote(noteId, content) {
    try {
        const response = await fetch(`/api/notes/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to update note');
        }
        
        showFlashMessage('Note updated successfully!', 'success');
        return data;
    } catch (error) {
        console.error('Error updating note:', error);
        showFlashMessage(error.message, 'danger');
        return null;
    }
}

// Attendee CRUD examples
async function createAttendee(meetingId, name, email) {
    try {
        const response = await fetch('/api/attendees', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                meeting_id: meetingId,
                name: name,
                email: email
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to add attendee');
        }
        
        showFlashMessage('Attendee added successfully!', 'success');
        return data;
    } catch (error) {
        console.error('Error adding attendee:', error);
        showFlashMessage(error.message, 'danger');
        return null;
    }
}

async function deleteAttendeeAPI(attendeeId) {
    try {
        const response = await fetch(`/api/attendees/${attendeeId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to remove attendee');
        }
        
        showFlashMessage('Attendee removed successfully!', 'success');
        return data;
    } catch (error) {
        console.error('Error removing attendee:', error);
        showFlashMessage(error.message, 'danger');
        return null;
    }
}

// Utility functions
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Export functions for use in other scripts (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showFlashMessage,
        fetchMeetings,
        createMeeting,
        updateMeeting,
        deleteMeetingAPI,
        createNote,
        updateNote,
        createAttendee,
        deleteAttendeeAPI,
        formatDateTime,
        formatDate
    };
}
