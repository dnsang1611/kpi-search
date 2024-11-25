"use client"

import React from 'react';
import Gallery from "@/_components/Gallery";
import Sidebar from "@/_components/Sidebar";
import store from '@/_store/store';
import { Provider } from 'react-redux';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'

export default function Home() {
  return (
    <Provider store={store}>
      <div className='flex bg-blue-100'>
        <Sidebar />
        <Gallery />
      </div>
      <ToastContainer
        toastClassName='relative flex min-h-10 rounded-md justify-between overflow-hidden w-max cursor-pointer'
        bodyClassName={() => 'font-white font-medium block p-3 flex gap-1 w-full'}
        position='bottom-left'
        autoClose={2000}
        pauseOnHover={false}
      />    
      </Provider>
  );
}