import ImageGallery from "./components/ImageGallery";
import SideBar from "./components/SideBar";
import SessionProvider from "./components/SessionContext";

const App = () => {
  return <div>
    <SessionProvider>
      <div className="flex">
        <SideBar />
        <ImageGallery />
      </div>
    </SessionProvider>
  </div>
}

export default App;