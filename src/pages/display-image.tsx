import { useRouter } from 'next/router';

export default function DisplayImage() {
  const router = useRouter();
  const imageUrl = decodeURIComponent(router.query.image_url as string);

  return (
    <div>
      <img src={imageUrl} alt="Generated" />
    </div>
  );
}