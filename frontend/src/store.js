import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const fetchInteractions = createAsyncThunk('interactions/fetch', async () => {
  const response = await axios.get(`${API_URL}/interactions/`);
  return response.data;
});

export const addInteraction = createAsyncThunk('interactions/add', async (interaction) => {
  const response = await axios.post(`${API_URL}/interactions/`, interaction);
  return response.data;
});

export const sendChatMessage = createAsyncThunk('chat/send', async (message) => {
  const response = await axios.post(`${API_URL}/chat/`, { message });
  return { message, response: response.data.response };
});

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    status: 'idle',
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.list = action.payload;
      })
      .addCase(addInteraction.fulfilled, (state, action) => {
        state.list.push(action.payload);
      });
  },
});

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [{ role: 'ai', content: 'Hello! I am your AI CRM assistant. How can I help you manage your HCP interactions today?' }],
    status: 'idle',
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({ role: 'user', content: action.payload });
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = 'idle';
        state.messages.push({ role: 'ai', content: action.payload.response });
      })
      .addCase(sendChatMessage.rejected, (state) => {
        state.status = 'error';
        state.messages.push({ role: 'ai', content: 'Sorry, an error occurred.' });
      });
  },
});

export const { addUserMessage } = chatSlice.actions;

export const store = configureStore({
  reducer: {
    interactions: interactionSlice.reducer,
    chat: chatSlice.reducer,
  },
});
