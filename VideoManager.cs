using UnityEngine;
using UnityEngine.Video;
using System.Collections.Generic;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using TMPro;

public class VideoManager : MonoBehaviour
{
    // Video Player
    public VideoPlayer mainVideoPlayer;
    public VideoClip mainClip;
    //public VideoPlayer tempVideoPlayer;

    public List<VideoClip> happyClips;
    public List<VideoClip> angryClips;
    public List<VideoClip> sadClips;

    private bool isClipPlaying = false;

    private double mainVideoTime;

    private Dictionary<string, VideoList> videoLists = new Dictionary<string, VideoList>();

    // Text For Clips
    public TextMeshProUGUI text;

    // UDP Connection
    private Thread receiveThread;
    private UdpClient client;
    IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
    public int port = 5505;
    public bool startRecieving = true;
    public bool printToConsole = true;
    public string data;
    private byte[] sendData = {0x07};

    private class VideoList
    {
        public List<VideoClip> clips;
        public int currentIndex;
         
        public VideoClip GetNextClip()
        {
            if (clips == null || clips.Count == 0)
                return null;

            VideoClip clip = clips[currentIndex];
            currentIndex = (currentIndex + 1) % clips.Count;  // Loop
            return clip;
        }
    }

    void PreloadAllClips()
    {
        // VideoPlayer doesn't "preload" in the usual sense, but you can Prepare() clips
        // This step is optional and may improve responsiveness on some platforms
        foreach (var list in videoLists.Values)
        {
            foreach (var clip in list.clips)
            {
                // If you're using Addressables or AssetBundles, this is where you would preload them.
                // In the Editor or Resources, just referencing them is enough.
            }
        }
    }

    void Start()
    {
        // Initialize and preload clip sets
        videoLists["happyClips"] = new VideoList { clips = happyClips, currentIndex = 0 };
        videoLists["angryClips"] = new VideoList { clips = angryClips, currentIndex = 0 };
        videoLists["sadClips"] = new VideoList { clips = sadClips, currentIndex = 0 };

        // Optionally pre-prepare all clips (for faster loading)
        PreloadAllClips();

        // Set the text to not be active in the scene
        text.gameObject.SetActive(false);

        // Play main video
        mainVideoPlayer.clip = mainClip;
        mainVideoPlayer.isLooping = true;
        mainVideoPlayer.Play();

        // UDP Connection setup
        client = new UdpClient(port);
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    void Update()
    {
        if (!string.IsNullOrEmpty(data) && !isClipPlaying)
        {
            PlayClip(data);
        }
    }

    private void ReceiveData()
    {
        while(startRecieving)
        {
            try
            {
                byte[] dataByte = client.Receive(ref anyIP);
                data = Encoding.UTF8.GetString(dataByte);

                if(printToConsole)
                {
                    print(data);
                }
            }
            catch (Exception err)
            {
                Debug.LogError(err.ToString());
            }
        }
    }

    // Call this method when the trigger happens
    public void PlayClip (string _data)
    {
        if (!isClipPlaying)
        {
            StartCoroutine(PlayTemporaryVideo(_data));
        }
    }

    private System.Collections.IEnumerator PlayTemporaryVideo(string triggerName)
    {
        // reset so it doesn't keep triggering the last data sent
        data = null;

        if (!videoLists.ContainsKey(triggerName))
        {
            Debug.LogWarning($"No list found for trigger '{triggerName}'");
            yield break;
        }

        VideoClip nextClip = videoLists[triggerName].GetNextClip();

        if (nextClip == null)
        {
            Debug.LogWarning($"No video clip found in trigger '{triggerName}'");
            yield break;
        }

        isClipPlaying = true;
        mainVideoPlayer.loopPointReached += OnTempVideoEnd;

        mainVideoTime = mainVideoPlayer.time;
        mainVideoPlayer.Pause();

        if(triggerName == "happyClips")
        {
            text.text = "happy / content";
        } else if (triggerName == "sadClips")
        {
            text.text = "anxious / worried";
        } else if(triggerName == "angryClips")
        {
            text.text = "angry / irritated";
        }
        text.gameObject.SetActive(true);

        mainVideoPlayer.clip = nextClip;
        mainVideoPlayer.isLooping = false;
        mainVideoPlayer.Play();

        yield return null;
    }

    private void OnTempVideoEnd(VideoPlayer vp)
    {
        mainVideoPlayer.loopPointReached -= OnTempVideoEnd;
        mainVideoPlayer.Stop();
        mainVideoPlayer.clip = mainClip;
        mainVideoPlayer.time = mainVideoTime;
        mainVideoPlayer.isLooping = true;
        mainVideoPlayer.Play();

        isClipPlaying = false;
        text.gameObject.SetActive(false);

        try
        {
            client.Send(sendData, sendData.Length, anyIP);
            Debug.Log("Data sent to Python.");
        }
        catch (Exception err)
        {
            Debug.LogError(err.ToString());
        }
    }

    private void OnApplicationQuit()
    {
        if(receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Abort();
        }
        if(client != null)
        {
            client.Close();
        }
    }
}
