import { configureStore } from '@reduxjs/toolkit';
import searchReducer from './slices/searchSlice';
import imageSearchReducer from './slices/imageSearchSlice'
import rerankReducer from './slices/rerankSlice'

const store = configureStore({
  reducer: {
    search: searchReducer,
    imageSearch: imageSearchReducer,
    rerank: rerankReducer
  },
});

export default store;
