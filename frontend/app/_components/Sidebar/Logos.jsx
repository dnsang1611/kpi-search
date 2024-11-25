import Image from "next/image";

export const images = [
    {
        id: 1,
        title: "UIT",
        src: "/aic2024/uit.svg"
    },
    {
        id: 2,
        title: "CS",
        src: "/aic2024/cs.svg"
    },
    {
        id: 3,
        title: "MMLab",
        src: "/aic2024/mmlab.svg"
    }
]

const Logos = () => {
    return (
        <div className="flex gap-4 py-2 px-4 bg-white rounded-full mt-1 size-fit">
            {images.map(({ id, title, src }) => (
                <Image src={src} key={id} alt={title} height={0} width={0} className="object-contain h-6 w-8"/>
            ))}
        </div>
    )
}

export default Logos;