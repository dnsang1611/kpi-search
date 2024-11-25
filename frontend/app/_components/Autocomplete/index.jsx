import { useState, useEffect } from 'react';

const Autocomplete = ({ options, value, onChange }) => {
  const [inputValue, setInputValue] = useState(value || '');
  const [filteredOptions, setFilteredOptions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  useEffect(() => {
    if (showDropdown && inputValue) {
      setFilteredOptions(
        options.filter((option) =>
          option.toLowerCase().includes(inputValue.toLowerCase())
        )
      );
    } else if (showDropdown) {
      setFilteredOptions(options);
    } else {
      setFilteredOptions([]);
    }
  }, [inputValue, options, showDropdown]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    setShowDropdown(true);
  };

  const handleOptionClick = (option) => {
    setInputValue(option);
    onChange(option);
    setShowDropdown(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      setHighlightedIndex((prevIndex) =>
        prevIndex < filteredOptions.length - 1 ? prevIndex + 1 : prevIndex
      );
    } else if (e.key === 'ArrowUp') {
      setHighlightedIndex((prevIndex) =>
        prevIndex > 0 ? prevIndex - 1 : prevIndex
      );
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredOptions.length > 0) {
        handleOptionClick(filteredOptions[highlightedIndex]);
      }
    }
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        onFocus={() => setShowDropdown(true)}
        onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
        onKeyDown={handleKeyDown}
        className="p-2 w-full placeholder:text-sm border-b border-slate-500 outline-none"
        placeholder="Select an object"
      />
      {showDropdown && (
        <ul className="absolute z-10 bg-white rounded w-full max-h-56 overflow-y-auto shadow-md">
          {filteredOptions.map((option, index) => (
            <li
              key={index}
              onClick={() => handleOptionClick(option)}
              className={`p-2 cursor-pointer hover:bg-blue-50 ${
                index === highlightedIndex ? 'bg-blue-50' : ''
              }`}
            >
              {option}
            </li>
          ))}
          {filteredOptions.length === 0 && (
            <li className="p-2 text-gray-500">No options</li>
          )}
        </ul>
      )}
    </div>
  );
};

export default Autocomplete;
