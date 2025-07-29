using UnityEngine;
using System;
using System.Runtime.InteropServices;

public class DisplayManager : MonoBehaviour
{
    [DllImport("user32.dll")]
    static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr lprcClip,
          MonitorEnumProc lpfnEnum, IntPtr dwData);

    [DllImport("user32.dll")]
    static extern bool GetMonitorInfo(IntPtr hMonitor, ref MONITORINFO lpmi);

    [DllImport("user32.dll")]
    static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    static extern bool MoveWindow(IntPtr hWnd, int x, int y, int nWidth, int nHeight, bool bRepaint);

    [DllImport("user32.dll")]
    static extern int SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);

    [DllImport("user32.dll")]
    static extern uint GetWindowLong(IntPtr hWnd, int nIndex);

    delegate bool MonitorEnumProc(IntPtr hMonitor, IntPtr hdcMonitor, ref RECT lprcMonitor, IntPtr dwData);

    const int GWL_STYLE = -16;
    const uint WS_POPUP = 0x80000000;
    const uint WS_VISIBLE = 0x10000000;

    void MakeBorderless(IntPtr hWnd)
    {
        uint style = WS_POPUP | WS_VISIBLE;
        SetWindowLong(hWnd, GWL_STYLE, style);
    }

    [StructLayout(LayoutKind.Sequential)]
    struct RECT
    {
        public int left, top, right, bottom;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    struct MONITORINFO
    {
        public int cbSize;
        public RECT rcMonitor;
        public RECT rcWork;
        public uint dwFlags;
    }

    void Start()
    {
        StartCoroutine(MoveWindowToSecondaryMonitor());
    }

    System.Collections.IEnumerator MoveWindowToSecondaryMonitor()
    {
        yield return new WaitForSeconds(0.5f); // Wait for window creation

        IntPtr hWnd = FindWindow(null, Application.productName);
        if (hWnd == IntPtr.Zero)
        {
            Debug.LogError("Cannot find Unity window handle.");
            yield break;
        }

        IntPtr secondaryMonitorHandle = IntPtr.Zero;
        int displayIndex = 1; // second monitor (0-based)

        // Enumerate monitors to find secondary monitor handle
        int currentIndex = 0;
        EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero,
            (IntPtr hMonitor, IntPtr hdcMonitor, ref RECT lprcMonitor, IntPtr dwData) =>
            {
                if (currentIndex == displayIndex)
                {
                    secondaryMonitorHandle = hMonitor;
                    return false; // stop enumeration
                }
                currentIndex++;
                return true; // continue
            }, IntPtr.Zero);

        if (secondaryMonitorHandle == IntPtr.Zero)
        {
            Debug.LogError("Secondary monitor handle not found.");
            yield break;
        }

        MONITORINFO mi = new MONITORINFO();
        mi.cbSize = Marshal.SizeOf(typeof(MONITORINFO));

        if (GetMonitorInfo(secondaryMonitorHandle, ref mi))
        {
            int width = mi.rcMonitor.right - mi.rcMonitor.left;
            int height = mi.rcMonitor.bottom - mi.rcMonitor.top;

            Debug.Log($"Secondary monitor bounds: {mi.rcMonitor.left}, {mi.rcMonitor.top}, {width}x{height}");
            MakeBorderless(hWnd);
            // Move window to secondary monitor full bounds
            MoveWindow(hWnd, mi.rcMonitor.left, mi.rcMonitor.top, width, height, true);
        }
        else
        {
            Debug.LogError("Failed to get monitor info.");
        }
    }
}
