/**
 * Ticket Redux Slice
 *
 * State management for ticket operations
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { ticketApi } from '@/api/endpoints/ticket.api'
import type {
  Ticket,
  TicketCreate,
  TicketUpdate,
  TicketFilters,
  TicketSortOptions,
  TicketListParams,
  UpdateStatusRequest,
  ResolveTicketRequest,
  CloseTicketRequest,
  ReopenTicketRequest,
  TicketState,
} from '@/types/ticket.types'

// ============================================================================
// Initial State
// ============================================================================

const initialState: TicketState = {
  tickets: [],
  selectedTicket: null,
  filters: {},
  sortOptions: {
    sort_by: 'created_at',
    order: 'desc',
  },
  pagination: {
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  },
  loading: false,
  error: null,
}

// ============================================================================
// Async Thunks
// ============================================================================

/**
 * Fetch tickets with filters, sorting, pagination
 */
export const fetchTickets = createAsyncThunk(
  'ticket/fetchTickets',
  async (params: TicketListParams | undefined, { rejectWithValue }) => {
    try {
      const response = await ticketApi.list(params)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch tickets')
    }
  }
)

/**
 * Fetch ticket by ID
 */
export const fetchTicketById = createAsyncThunk(
  'ticket/fetchTicketById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await ticketApi.getById(id)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch ticket')
    }
  }
)

/**
 * Create new ticket
 */
export const createTicket = createAsyncThunk(
  'ticket/createTicket',
  async (data: TicketCreate, { rejectWithValue }) => {
    try {
      const response = await ticketApi.create(data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create ticket')
    }
  }
)

/**
 * Update ticket (full update)
 */
export const updateTicket = createAsyncThunk(
  'ticket/updateTicket',
  async ({ id, data }: { id: string; data: TicketUpdate }, { rejectWithValue }) => {
    try {
      const response = await ticketApi.update(id, data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update ticket')
    }
  }
)

/**
 * Patch ticket (partial update)
 */
export const patchTicket = createAsyncThunk(
  'ticket/patchTicket',
  async ({ id, data }: { id: string; data: Partial<TicketUpdate> }, { rejectWithValue }) => {
    try {
      const response = await ticketApi.patch(id, data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to patch ticket')
    }
  }
)

/**
 * Delete ticket
 */
export const deleteTicket = createAsyncThunk(
  'ticket/deleteTicket',
  async (id: string, { rejectWithValue }) => {
    try {
      await ticketApi.delete(id)
      return id
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete ticket')
    }
  }
)

// ============================================================================
// Workflow Thunks
// ============================================================================

/**
 * Change ticket status
 */
export const changeTicketStatus = createAsyncThunk(
  'ticket/changeStatus',
  async ({ id, data }: { id: string; data: UpdateStatusRequest }, { rejectWithValue }) => {
    try {
      const response = await ticketApi.changeStatus(id, data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to change status')
    }
  }
)

/**
 * Resolve ticket
 */
export const resolveTicket = createAsyncThunk(
  'ticket/resolveTicket',
  async ({ id, data }: { id: string; data: ResolveTicketRequest }, { rejectWithValue }) => {
    try {
      const response = await ticketApi.resolve(id, data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to resolve ticket')
    }
  }
)

/**
 * Close ticket
 */
export const closeTicket = createAsyncThunk(
  'ticket/closeTicket',
  async ({ id, data }: { id: string; data: CloseTicketRequest }, { rejectWithValue }) => {
    try {
      const response = await ticketApi.close(id, data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to close ticket')
    }
  }
)

/**
 * Reopen ticket
 */
export const reopenTicket = createAsyncThunk(
  'ticket/reopenTicket',
  async ({ id, data }: { id: string; data: ReopenTicketRequest }, { rejectWithValue }) => {
    try {
      const response = await ticketApi.reopen(id, data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to reopen ticket')
    }
  }
)

// ============================================================================
// Ticket Slice
// ============================================================================

const ticketSlice = createSlice({
  name: 'ticket',
  initialState,
  reducers: {
    // Set filters
    setFilters: (state, action: PayloadAction<TicketFilters>) => {
      state.filters = action.payload
      state.pagination.page = 1 // Reset to first page when filters change
    },

    // Update filters (merge with existing)
    updateFilters: (state, action: PayloadAction<Partial<TicketFilters>>) => {
      state.filters = { ...state.filters, ...action.payload }
      state.pagination.page = 1
    },

    // Clear filters
    clearFilters: (state) => {
      state.filters = {}
      state.pagination.page = 1
    },

    // Set sort options
    setSortOptions: (state, action: PayloadAction<TicketSortOptions>) => {
      state.sortOptions = action.payload
    },

    // Set pagination
    setPagination: (state, action: PayloadAction<Partial<typeof initialState.pagination>>) => {
      state.pagination = { ...state.pagination, ...action.payload }
    },

    // Set selected ticket
    setSelectedTicket: (state, action: PayloadAction<Ticket | null>) => {
      state.selectedTicket = action.payload
    },

    // Clear selected ticket
    clearSelectedTicket: (state) => {
      state.selectedTicket = null
    },

    // Clear error
    clearError: (state) => {
      state.error = null
    },

    // Reset state
    resetTicketState: () => initialState,
  },
  extraReducers: (builder) => {
    // Fetch Tickets
    builder
      .addCase(fetchTickets.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchTickets.fulfilled, (state, action) => {
        state.loading = false
        state.tickets = action.payload.tickets
        state.pagination = {
          page: action.payload.page,
          pageSize: action.payload.page_size,
          total: action.payload.total,
          totalPages: action.payload.total_pages,
        }
      })
      .addCase(fetchTickets.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Fetch Ticket By ID
    builder
      .addCase(fetchTicketById.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchTicketById.fulfilled, (state, action) => {
        state.loading = false
        state.selectedTicket = action.payload
      })
      .addCase(fetchTicketById.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Create Ticket
    builder
      .addCase(createTicket.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(createTicket.fulfilled, (state, action) => {
        state.loading = false
        state.tickets.unshift(action.payload) // Add to beginning
        state.pagination.total += 1
      })
      .addCase(createTicket.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Update Ticket
    builder
      .addCase(updateTicket.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(updateTicket.fulfilled, (state, action) => {
        state.loading = false
        // Update in list
        const index = state.tickets.findIndex((t) => t.id === action.payload.id)
        if (index !== -1) {
          state.tickets[index] = action.payload
        }
        // Update selected ticket if it matches
        if (state.selectedTicket?.id === action.payload.id) {
          state.selectedTicket = action.payload
        }
      })
      .addCase(updateTicket.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Patch Ticket
    builder
      .addCase(patchTicket.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(patchTicket.fulfilled, (state, action) => {
        state.loading = false
        const index = state.tickets.findIndex((t) => t.id === action.payload.id)
        if (index !== -1) {
          state.tickets[index] = action.payload
        }
        if (state.selectedTicket?.id === action.payload.id) {
          state.selectedTicket = action.payload
        }
      })
      .addCase(patchTicket.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Delete Ticket
    builder
      .addCase(deleteTicket.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(deleteTicket.fulfilled, (state, action) => {
        state.loading = false
        state.tickets = state.tickets.filter((t) => t.id !== action.payload)
        state.pagination.total -= 1
        if (state.selectedTicket?.id === action.payload) {
          state.selectedTicket = null
        }
      })
      .addCase(deleteTicket.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Change Status
    builder
      .addCase(changeTicketStatus.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(changeTicketStatus.fulfilled, (state, action) => {
        state.loading = false
        const index = state.tickets.findIndex((t) => t.id === action.payload.id)
        if (index !== -1) {
          state.tickets[index] = action.payload
        }
        if (state.selectedTicket?.id === action.payload.id) {
          state.selectedTicket = action.payload
        }
      })
      .addCase(changeTicketStatus.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Resolve Ticket
    builder
      .addCase(resolveTicket.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(resolveTicket.fulfilled, (state, action) => {
        state.loading = false
        const index = state.tickets.findIndex((t) => t.id === action.payload.id)
        if (index !== -1) {
          state.tickets[index] = action.payload
        }
        if (state.selectedTicket?.id === action.payload.id) {
          state.selectedTicket = action.payload
        }
      })
      .addCase(resolveTicket.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Close Ticket
    builder
      .addCase(closeTicket.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(closeTicket.fulfilled, (state, action) => {
        state.loading = false
        const index = state.tickets.findIndex((t) => t.id === action.payload.id)
        if (index !== -1) {
          state.tickets[index] = action.payload
        }
        if (state.selectedTicket?.id === action.payload.id) {
          state.selectedTicket = action.payload
        }
      })
      .addCase(closeTicket.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Reopen Ticket
    builder
      .addCase(reopenTicket.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(reopenTicket.fulfilled, (state, action) => {
        state.loading = false
        const index = state.tickets.findIndex((t) => t.id === action.payload.id)
        if (index !== -1) {
          state.tickets[index] = action.payload
        }
        if (state.selectedTicket?.id === action.payload.id) {
          state.selectedTicket = action.payload
        }
      })
      .addCase(reopenTicket.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
  },
})

export const {
  setFilters,
  updateFilters,
  clearFilters,
  setSortOptions,
  setPagination,
  setSelectedTicket,
  clearSelectedTicket,
  clearError,
  resetTicketState,
} = ticketSlice.actions

export default ticketSlice.reducer
