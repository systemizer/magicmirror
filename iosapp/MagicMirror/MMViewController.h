//
//  MMViewController.h
//  MagicMirror
//
//  Created by Doug Feigelson on 7/21/12.
//  Copyright (c) 2012 MIT. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <AVFoundation/AVFoundation.h>
#import <RestKit/RestKit.h>

@interface MMViewController : UIViewController <AVAudioRecorderDelegate, RKRequestDelegate, UIWebViewDelegate, UIScrollViewDelegate> {
    NSString* recordingFilePath;
    NSArray* modes;
}

@property AVAudioRecorder* recorder; 
@property UIWebView* webView;
@property UIWebView* replacementWebView;
@property UIScrollView* scrollView;
@property NSString* contentMode;

@end
