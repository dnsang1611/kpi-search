def timestamp_to_frame(timestamp: str, fps=25, separator=";") -> int:
    """
    Convert a timestamp to a frame number.
    """
    # convert timestamp to seconds
    timestamp_parts = timestamp.split(separator)
    hours = int(timestamp_parts[0])
    minutes = int(timestamp_parts[1])
    seconds = int(timestamp_parts[2])

    num_sec = hours * 3600 + minutes * 60 + seconds

    # convert seconds to frame number
    return int(num_sec * fps)
